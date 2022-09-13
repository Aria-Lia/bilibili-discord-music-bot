import discord
import io
import re
import requests
import subprocess
import shlex
import traceback
from discord.opus import Encoder

video_info_url = u'http://api.bilibili.com/x/web-interface/view?bvid={}'
stream_url = u'http://api.bilibili.com/x/player/playurl?bvid={}&cid={}&fnval=16'
EMBED_COLOR = '#ffb882'


class FFmpegPCMAudio(discord.AudioSource):
    # https://github.com/Rapptz/discord.py/issues/5192
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        stdin = None if not pipe else source
        args = [executable]
        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))
        if isinstance(options, str):
            args.extend(shlex.split(options))
        args.append('pipe:1')
        self._process = None
        try:
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
            self._stdout = io.BytesIO(
                self._process.communicate(input=stdin)[0]
            )
        except FileNotFoundError:
            raise discord.ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as exc:
            raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc

    def read(self):
        ret = self._stdout.read(Encoder.FRAME_SIZE)
        if len(ret) != Encoder.FRAME_SIZE:
            return b''
        return ret

    def cleanup(self):
        proc = self._process
        if proc is None:
            return
        proc.kill()
        if proc.poll() is None:
            proc.communicate()

        self._process = None


def get_bv_id_from_url(url):
    if not url:
        return

    result = re.search('BV.{10}', url)
    if result:
        return result.group(0)


def get_cid_from_bv_id(_id):
    try:
        response = requests.get(video_info_url.format(_id)).json()
        data = response['data']
        title, cid = data['title'], data['cid']
        description = data['desc_v2'][0]['raw_text'] if data['desc_v2'] else data['desc']
        author = data['owner']['name'] if data['owner'] else None

        return title, cid, description, author
    except Exception as e:
        print('get_cid_from_bv_id', e)
        return


def get_audio_url_from_bv_id(_id, cid):
    try:
        response = requests.get(stream_url.format(_id, cid)).json()
        audio = response['data']['dash']['audio']
        audio.sort(key=lambda x: x['bandwidth'])

        return audio[0]['baseUrl']
    except Exception as e:
        print('get_audio_url_from_bv_id', e)
        return


def get_discord_mpeg_audio_from_audio_url(url):
    try:
        response = requests.get(url, stream=True)
        data = io.BytesIO(response.content)

        return FFmpegPCMAudio(data.read(), pipe=True)
    except Exception as e:
        print('get_discord_mpeg_audio_from_audio_url', traceback.format_exc(), e)
        return


def get_discord_embed(author, **kwargs):
    embed = discord.Embed(type='rich', colour=discord.Colour.from_str(EMBED_COLOR), **kwargs)
    embed.set_author(name=author)

    return embed


if __name__ == "__main__":
    test = 'https://www.bilibili.com/video/BV1Lr4y1w73P'
    expected = 'BV1Lr4y1w73P'
    actual = get_bv_id_from_url(test)
    assert actual == expected

    test = 'https://www.bilibili.com/video/BV1Ev411V7D2?spm_id_from=333.851.b_7265636f6d6d656e64.3'
    expected = 'BV1Ev411V7D2'
    actual = get_bv_id_from_url(test)
    assert actual == expected

    test = ''
    expected = None
    actual = get_bv_id_from_url(test)
    assert actual == expected

    test = 'https://www.bilibili.com/video/BV1Ev'
    expected = None
    actual = get_bv_id_from_url(test)
    assert actual == expected

    test = 'BV1Lr4y1w73P'
    expected = 248481897
    actual = get_cid_from_bv_id(test)
    assert len(actual) == 2
    assert len(actual[0]) > 0
    assert actual[1] == expected

    test = ['BV1Lr4y1w73P', 248481897]
    actual = get_audio_url_from_bv_id(*test)
    assert actual is not None

    test = get_audio_url_from_bv_id('BV1Lr4y1w73P', 248481897)
    actual = get_discord_mpeg_audio_from_audio_url(test)
    assert actual is not None
