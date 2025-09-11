# coding: utf-8
import m3u8
import requests


def redirected_resolution_url(
        url: str,
        headers: dict = None,
        verify_ssl: bool = False,
        timeout: int = 10
):
    """
    从 m3u8 文件获取重定向的解析URL.
    :param url: m3u8文件 URL.
    :param headers: 请求头.
    :param verify_ssl: 是否验证SSL证书.
    :param timeout: 超时时间.
    :return: 重定向的解析 URL.
    """
    print(f'从 {url} 获取重定向的解析URL')
    headers = headers or {}
    m3u8_obj = m3u8.load(url, headers=headers, verify_ssl=verify_ssl, timeout=timeout)
    __max_resolution = (0, 0)
    max_index = -1
    # 找到最大分辨率的播放列表
    playlists = m3u8_obj.playlists
    playlist: m3u8.Playlist
    print(f'找到 {len(playlists)} 个播放列表, 开始查找最大分辨率的播放列表')
    if not playlists:
        return None
    for i, playlist in enumerate(playlists):
        resolution = playlist.stream_info.resolution
        if not resolution:
            break
        if resolution > __max_resolution:
            __max_resolution = resolution
            max_index = i
    print(f'最大分辨率的播放列表为 {max_index}')
    max_url = m3u8_obj.playlists[max_index].absolute_uri
    print(f'最大分辨率的播放列表的 URL 为 {max_url}')
    return max_url


def m3u8_to_absolute_uris(
        url: str,
        headers: dict = None,
        verify_ssl: bool = False,
        timeout: int = 10
):
    """
    从 m3u8 文件获取重定向的解析 URL 列表.
    :param url: m3u8文件 URL.
    :param headers: 请求头.
    :param verify_ssl: 是否验证SSL证书.
    :param timeout: 超时时间.
    :return: 重定向的解析URL列表.
    """
    print('将 m3u8 文件转换为绝对 URL 列表，并获取加密密钥信息')
    headers = headers or {}
    m3u8_obj = m3u8.load(url, headers=headers, verify_ssl=verify_ssl, timeout=timeout)
    absolute_uris = []
    kt: m3u8.Key = m3u8_obj.segments[0].key
    key = {
        'key': '',
        'method': '',
        'uri': '',
        'iv': '',
        'keyformat': '',
        'keyformatversions': ''
    }
    if kt:
        response = requests.get(kt.absolute_uri, headers=headers, verify=verify_ssl)
        response.raise_for_status()
        iv = kt.iv
        if iv:
            iv = iv[2:18]
        key = {
            'key': response.content,
            'method': kt.method,
            'uri': kt.absolute_uri,
            'iv': iv,
            'keyformat': kt.keyformat,
            'keyformatversions': kt.keyformatversions
        }
        print(f'加密密钥信息: {key}')
    else:
        print('未找到加密密钥信息')
    print(f'找到 {len(m3u8_obj.segments)} 个分段, 开始获取绝对 URL 列表')
    for segment in m3u8_obj.segments:
        segment: m3u8.Segment
        absolute_uris.append(segment.absolute_uri)
    return absolute_uris, key
