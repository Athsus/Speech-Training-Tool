import re


def parse_result(text, result):
    """
    :return: (tuple) (HTML_formed str, innder list of result)
    """
    corrections = []
    for error_type, items in result.items():
        for item in items:
            corrections.append((item[0], len(item[1]),
                                f'<span style="background-color:rgba(245, 204, 8, 122);" data-error-type="{error_type}">{item[1]}</span>'))
    corrections.sort(key=lambda x: x[0], reverse=True)  # 很妙的排序

    # 替换文本
    for start, length, content in corrections:
        text = text[:start] + content + text[start + length:]

    # 把result所以key对应的value的list的items提取出来，成为一个list
    result_sub_list = [item for items in result.values() for item in items]

    return text, result_sub_list


def extract_error_positions(html_text):
    error_positions = []
    for match in re.finditer('<span style="background-color:rgba(245, 204, 8, 122);" data-error-type="([^"]+)">([^<]+)</span>',
                             html_text):
        error_type, word = match.groups()
        start_pos = match.start(2)
        error_positions.append((start_pos, len(word), error_type))

    return error_positions