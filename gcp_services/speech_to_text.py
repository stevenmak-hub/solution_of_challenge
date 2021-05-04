import io
from google.cloud import speech_v1p1beta1 as speech

class SpeechToText:
    def __init__(self):
        pass

    def _get_file_type(self):
        return self.speech_file.split('.')[-1]

    def _get_recognition_config_params(self, frameRate = None):
        fileType = self._get_file_type()
        if fileType == 'flac':
            self.recogConfig = dict(
                encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
                audio_channel_count=2,
                language_code='yue-Hant-HK'
            )
        elif fileType == 'mp3':
            self.recogConfig = dict(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                language_code='yue-Hant-HK'
            )
        elif fileType == 'wav':
            self.recogConfig = dict(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                use_enhanced = True,
                language_code='yue-Hant-HK'
            )
        if frameRate is not None:
            self.recogConfig['sample_rate_hertz'] = frameRate
        self.recogConfig['use_enhanced'] = True
        self.recogConfig['max_alternatives'] = 1

        return self.recogConfig

    def transcribe_from_file(self, speech_file, frameRate = None):
        self.speech_file = speech_file
        client = speech.SpeechClient()
        with io.open(speech_file, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(self._get_recognition_config_params(frameRate))
        operation = client.long_running_recognize(config=config, audio=audio)
        # print("Waiting for operation to complete...")
        response = operation.result()
        print(f'result length: {len(response.results)}')

        if len(response.results) >= 1:
            result = {
                'Transcript': response.results[0].alternatives[0].transcript,
                'Confidence': response.results[0].alternatives[0].confidence
            }
        else:
            result = {'Transcript': None, 'Confidence': None}
        return result

    def transcribe_gcs(gcs_uri):
        """Asynchronously transcribes the audio file specified by the gcs_uri."""
        client = speech.SpeechClient()

        audio = speech.types.RecognitionAudio(uri=gcs_uri)
        config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            audio_channel_count=2,
            enable_speaker_diarization=True,
            enable_word_time_offsets=True,
            diarization_speaker_count=2,
            max_alternatives=30,
            enable_separate_recognition_per_channel=True,
            language_code='yue-Hant-HK')

        response = client.long_running_recognize(config, audio)

        print('Waiting for operation to complete...')
        response = response.result(timeout=360)
        result = {
            'Transcript': response.results[0].alternatives[0].transcript,
            'Confidence': response.results[0].alternatives[0].confidence
        }
        return result

