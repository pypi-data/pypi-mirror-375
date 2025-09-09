from dataclasses import dataclass, field
from fractions import Fraction
from itertools import chain
import av
import av.stream
import av.video
import numpy as np

from smartcut.nal_tools import get_h264_nal_unit_type, get_h265_nal_unit_type, is_safe_h264_keyframe_nal, is_safe_h265_keyframe_nal

def ts_to_time(ts):
    return Fraction(round(ts*1000), 1000)

@dataclass
class AudioTrack():
    media_container: object
    av_stream: av.stream.Stream
    audio_load_stream: av.stream.Stream
    path: str
    index: int

    index_in_source: int = 0

    packets: list[av.Packet] = field(default_factory = lambda: [])
    frame_times: np.array = field(default_factory = lambda: [])
    pts_to_samples: dict = field(default_factory = lambda: {})

    controls: object = None
    error_msg: str = None
    audio_16k: np.array = None

    eof_time: Fraction = None
    shift: float = 0.0
    max_tree: np.array = None

    level_ignoring_mute: float = None
    muted: bool = None

    def selected_for_transcript(self):
        return self.controls is None or self.controls.transcript_button.isChecked()

    def duration(self) -> Fraction:
        return self.eof_time - self.media_container.start_time

    def start_time(self) -> Fraction:
        return self.media_container.start_time

class MediaContainer:
    av_containers: list[av.container.Container]
    video_stream: av.video.stream.VideoStream | None
    path: str

    eof_time: Fraction

    video_stream: av.stream.Stream | None

    video_frame_times: np.ndarray
    video_keyframe_indices: list[int]
    gop_start_times_pts_s: list[int] # Smallest pts in a GOP, in seconds

    gop_start_times_dts: list[int]
    gop_end_times_dts: list[int]
    gop_start_nal_types: list[int | None]  # NAL type of first picture frame after each GOP boundary

    audio_tracks: list[AudioTrack]
    subtitle_tracks: list

    chat_url: str | None
    chat_history: np.ndarray | None
    chat_cumsum: np.ndarray | None
    chat_visualize: bool

    def __init__(self, path, progress_callback=None) -> None:
        self.path = path

        frame_pts = []
        self.video_keyframe_indices = []

        est_eof_time = 0
        av_container = av.open(path, 'r', metadata_errors='ignore')
        audio_loading_container = av.open(path, 'r', metadata_errors='ignore')
        self.av_containers = [av_container, audio_loading_container]

        self.chat_url = None
        self.chat_history = None
        self.chat_visualize = True
        self.start_time = 0

        is_h264 = False
        is_h265 = False

        if len(av_container.streams.video) == 0:
            self.video_stream = None
            streams = av_container.streams.audio
        else:
            self.video_stream = av_container.streams.video[0]
            self.video_stream.thread_type = "FRAME"
            streams = [self.video_stream] + list(av_container.streams.audio)
            if self.video_stream.start_time is not None:
                self.start_time = self.video_stream.start_time * self.video_stream.time_base

            if self.video_stream.codec_context.name == 'hevc':
                is_h265 = True
            if self.video_stream.codec_context.name == 'h264':
                is_h264 = True

        self.audio_tracks = []
        stream_index_to_audio_track = {}
        for i, (a_s, loading_s) in enumerate(zip(av_container.streams.audio, audio_loading_container.streams.audio)):
            a_s.thread_type = "FRAME"
            loading_s.thread_type = "FRAME"
            track = AudioTrack(self, a_s, loading_s, path, i, i)
            self.audio_tracks.append(track)
            stream_index_to_audio_track[a_s.index] = track

        self.subtitle_tracks = []
        stream_index_to_subtitle_track = {}
        for i, s in enumerate(av_container.streams.subtitles):
            streams.append(s)
            stream_index_to_subtitle_track[s.index] = i
            self.subtitle_tracks.append([])

        video_keyframe_indices = []
        first_keyframe = True  # Always allow the first keyframe regardless of NAL type

        self.gop_start_times_dts = []
        self.gop_end_times_dts = []
        self.gop_start_nal_types = []
        last_seen_video_dts = -1

        # Progress tracking for demux loop
        packet_count = 0
        progress_report_interval = 1000  # Report progress every 1000 packets

        for packet in av_container.demux(streams):
            if packet.pts is None:
                continue
            est_eof_time = max(est_eof_time, (packet.pts + packet.duration) * packet.time_base)
            if packet.stream.type == 'video' and self.video_stream:

                if packet.is_keyframe:
                    nal_type = None
                    if is_h265:
                        nal_type = get_h265_nal_unit_type(bytes(packet))
                    elif is_h264:
                        nal_type = get_h264_nal_unit_type(bytes(packet))

                    # Always allow the first keyframe regardless of NAL type (may be SEI, parameter sets, etc.)
                    is_safe_keyframe = True
                    if first_keyframe:
                        first_keyframe = False  # Only apply to the very first keyframe
                    else:
                        # Use centralized helper functions for NAL type safety checks
                        if is_h265:
                            is_safe_keyframe = is_safe_h265_keyframe_nal(nal_type)
                        elif is_h264:
                            is_safe_keyframe = is_safe_h264_keyframe_nal(nal_type)
                    if is_safe_keyframe:
                        video_keyframe_indices.append(len(frame_pts))
                        dts = packet.dts if packet.dts is not None else -100_000_000
                        self.gop_start_times_dts.append(dts)
                        self.gop_start_nal_types.append(nal_type)

                        if last_seen_video_dts > 0:
                            self.gop_end_times_dts.append(last_seen_video_dts)
                last_seen_video_dts = packet.dts
                frame_pts.append(packet.pts)
            elif packet.stream.type == 'audio':
                track = stream_index_to_audio_track[packet.stream_index]
                track.last_packet = packet

                # NOTE: storing the audio packets like this keeps the whole compressed audio loaded in RAM
                track.packets.append(packet)
                track.frame_times.append(packet.pts)
            elif packet.stream.type == 'subtitle':
                self.subtitle_tracks[stream_index_to_subtitle_track[packet.stream_index]].append(packet)

            # Report progress periodically during demux
            packet_count += 1
            if progress_callback and packet_count % progress_report_interval == 0:
                # We can't know total packets in advance, so report based on time processed
                time_processed = float(est_eof_time) if est_eof_time > 0 else 0
                # Estimate progress as a percentage (this is approximate)
                if time_processed > 0:
                    progress_callback(int(min(90, time_processed * 10)), 100)  # Cap at 90% during demux

        # Adding 1ms of extra to make sure we include the last frame in the output
        self.eof_time = est_eof_time + Fraction(1, 1000)

        if self.video_stream is not None:
            self.gop_end_times_dts.append(last_seen_video_dts)
            self.video_frame_times = np.sort(np.array(frame_pts)) * self.video_stream.time_base

            self.gop_start_times_pts_s = list(self.video_frame_times[video_keyframe_indices])

            # Post-process: Fill in actual picture NAL types for HEVC parameter sets
            self._fill_hevc_picture_nal_types()

        for t in self.audio_tracks:
            frame_times = np.array(t.frame_times)
            t.frame_times = frame_times * t.av_stream.time_base
            # last_packet = t.packets[-1]
            last_packet = t.last_packet
            t.eof_time = (last_packet.pts + last_packet.duration) * last_packet.time_base

    def duration(self):
        return self.eof_time - self.start_time

    def _fill_hevc_picture_nal_types(self):
        """
        Post-process to fill in actual picture NAL types for HEVC GOPs that start with parameter sets.
        This does a second pass to look ahead after parameter sets to find the actual picture frames.
        """
        if not self.video_stream or self.video_stream.codec_context.name != 'hevc':
            return

        # Find indices that need to be filled (-1 placeholders)
        indices_to_fill = [i for i, nal_type in enumerate(self.gop_start_nal_types) if nal_type == -1]

        if not indices_to_fill:
            return  # Nothing to fill

        # Open a new container for the second pass
        av_container = av.open(self.path, 'r', metadata_errors='ignore')
        video_stream = av_container.streams.video[0]

        try:
            # Process sequentially through all keyframes, not just the target ones
            keyframe_index = 0
            indices_to_fill_set = set(indices_to_fill)
            looking_for_picture = False
            found_keyframes = 0
            found_pictures = 0

            for packet in av_container.demux(video_stream):
                if packet.pts is None or packet.stream.type != 'video':
                    continue

                # Check if this is a keyframe
                if packet.is_keyframe:
                    # Check if this keyframe corresponds to one we need to process
                    if keyframe_index in indices_to_fill_set:
                        # This is a parameter set keyframe that needs look-ahead
                        looking_for_picture = True
                        found_keyframes += 1
                    keyframe_index += 1
                    continue

                # If we're looking for a picture frame and found one
                if looking_for_picture and packet.stream.type == 'video':
                    nal_type = get_h265_nal_unit_type(bytes(packet))
                    if nal_type is not None and nal_type <= 21:  # All picture frames (0-21)
                        # Found the picture frame, record its NAL type
                        # Find which index in indices_to_fill this corresponds to
                        current_keyframe_idx = keyframe_index - 1  # We just processed this keyframe
                        if current_keyframe_idx in indices_to_fill_set:
                            # Find position in indices_to_fill list
                            list_position = indices_to_fill.index(current_keyframe_idx)
                            self.gop_start_nal_types[current_keyframe_idx] = nal_type
                            found_pictures += 1

                        looking_for_picture = False

                        if found_pictures >= len(indices_to_fill):
                            break  # All done

        finally:
            av_container.close()

    def close(self):
        for c in self.av_containers:
            c.close()

    def get_next_frame_time(self, t):
        t += self.start_time
        idx = np.searchsorted(self.video_frame_times, t)
        if idx == len(self.video_frame_times):
            return self.duration()
        elif idx == 0:
            return self.video_frame_times[0] - self.start_time
        # Otherwise, find the closest of the two possible candidates: arr[idx-1] and arr[idx]
        else:
            prev_val = self.video_frame_times[idx - 1]
            next_val = self.video_frame_times[idx]
            if t - prev_val <= next_val - t:
                return prev_val - self.start_time
            else:
                return next_val - self.start_time

    def add_audio_file(self, path):
        av_container = av.open(path, 'r', metadata_errors='ignore')
        self.av_containers.append(av_container)
        audio_load_container = av.open(path, 'r', metadata_errors='ignore')
        self.av_containers.append(audio_load_container)
        idx = 0
        stream = av_container.streams.audio[idx]
        stream.thread_type = "FRAME"
        audio_load_stream = audio_load_container.streams.audio[idx]
        audio_load_stream.thread_type = "FRAME"
        track = AudioTrack(self, stream, audio_load_stream, path, len(self.audio_tracks), 0)
        self.audio_tracks.append(track)

        est_eof_time = 0
        for packet in av_container.demux(stream):
            if packet.pts is None:
                continue
            est_eof_time = max(est_eof_time, (packet.pts + packet.duration) * packet.time_base)
            track.packets.append(packet)
            track.frame_times.append(packet.pts)

        if self.video_stream is None:
            self.eof_time = max(self.eof_time, est_eof_time)

        track.frame_times = np.array(track.frame_times)
        track.frame_times = track.frame_times * stream.time_base
        last_packet = track.packets[-1]
        track.eof_time = (last_packet.pts + last_packet.duration) * last_packet.time_base
        return track

class AudioReader:
    def __init__(self, track: AudioTrack, use_loading_stream: bool = False):
        self.track = track
        if use_loading_stream:
            self.stream = track.audio_load_stream
        else:
            self.stream = track.av_stream

        self.rate = self.stream.rate
        self.codec = self.stream.codec_context

        self.cache_time = -1
        self.packet_i = 0
        self.resampler = None

    def read(self, start, end) -> np.ndarray:
        start += self.track.start_time()
        end += self.track.start_time()
        dur = end - start
        buffer = np.zeros((round(self.stream.rate * dur), self.stream.channels), np.float32)
        start_in_samples = round(start * self.stream.rate)
        end_in_samples = start_in_samples + buffer.shape[0]

        # Decode 1 sec extra.
        # NOTE: TODO: This could be lower, but does it matter?
        start = np.searchsorted(self.track.frame_times, start - 1)

        self.codec.flush_buffers()

        first = True
        sample_pos = 0
        time_pos = -100
        for p in chain(self.track.packets[start:], [None]):
            # print(p)
            for f in self.codec.decode(p):
                f_start = f.pts * self.stream.time_base
                f_end = f_start + Fraction(f.samples, f.sample_rate)

                if first:
                    if f.pts in self.track.pts_to_samples:
                        sample_pos = self.track.pts_to_samples[f.pts]
                    else:
                        sample_pos = round(f_start * f.sample_rate)
                    # Set the sample position from the first non-negative packet.
                    # E.g. if packets are -23 & 0 dts: the 0 sets the sample position to 0
                    first = f.pts < 0
                elif abs(time_pos - f_start) > 0.04:
                    print(f'Skipping a gap in audio pts track: {self.track.index},  t:{float(time_pos):.1f}, t based on pts: {float(f_start):.1f}')
                    if f.pts in self.track.pts_to_samples:
                        sample_pos = self.track.pts_to_samples[f.pts]
                    else:
                        sample_pos = round(f_start * f.sample_rate)

                self.track.pts_to_samples[f.pts] = sample_pos
                if sample_pos >= end_in_samples:
                    break

                if sample_pos + f.samples > start_in_samples:
                    if f.format.name != 'fltp':
                        if self.resampler is None:
                            self.resampler = av.AudioResampler('fltp', f.layout, f.rate)
                        frames = self.resampler.resample(f)
                        # frames.extend(self.resampler.resample(None))
                        data = [rsf.to_ndarray() for rsf in frames]
                        decoded = np.concatenate(data, axis=-1)
                    else:
                        decoded = f.to_ndarray()
                    decoded = decoded.T
                    if sample_pos < start_in_samples:
                        decoded = decoded[start_in_samples - sample_pos:]
                        sample_pos = start_in_samples

                    l = min(end_in_samples - sample_pos, decoded.shape[0])
                    buffer_pos = sample_pos - start_in_samples
                    buffer[buffer_pos:buffer_pos+l] = decoded[:l]
                    sample_pos += decoded.shape[0]
                else:
                    sample_pos += f.samples
                time_pos = f_end
            else: # Break from the inner loop
                continue
            break

        return buffer.T

def layout_from_channels(channels):
    if channels == 1:
        return 'mono'
    if channels == 2:
        return 'stereo'
    if channels == 6:
        return '5.1'
    raise AssertionError("Invalid audio track layout. Some audio formats are not supported.")

def channels_from_layout(layout):
    match layout:
        case 'mono':
            return 1
        case 'stereo':
            return 2
        case '5.1':
            return 6
        case _:
            raise ValueError

def upmix(audio: np.array):
    if audio.shape[0] == 1:
        return np.repeat(audio, 2, axis=0)
    elif audio.shape[0] == 2:
        return np.concatenate([audio, np.zeros((4, audio.shape[0]))])
    raise ValueError

def downmix(audio: np.array):
    if audio.shape[0] == 2:
        return np.mean(audio, axis=0, keepdims=True)
    elif audio.shape[0] == 6:
        # 5.1 audio
        stereo = np.zeros((2, audio.shape[1]), dtype=np.float32)
        # Channels order: FL, FR, C, LFE, SL, SR
        # LFE is removed. Alternatively it could be mixed in at 0.1

        surround_channel_weight = 0.25
        center_weight = 0.5

        stereo[0] = audio[0] + audio[2] * center_weight + audio[4] * surround_channel_weight
        stereo[1] = audio[1] + audio[2] * center_weight + audio[5] * surround_channel_weight
        return stereo
    raise ValueError

def channel_conversion(audio: np.array, layout):
    c = audio.shape[0]
    target = channels_from_layout(layout)
    if c == target:
        return audio

    while c < target:
        audio = upmix(audio)
        c = audio.shape[0]
    while c > target:
        audio = downmix(audio)
        c = audio.shape[0]

    return audio
