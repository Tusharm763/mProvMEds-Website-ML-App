
def word_new_line_tag_html_safe(text, max_width=30):
    if not text:
        return ""

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        space_length = 1 if current_line else 0

        if current_length + space_length + word_length > max_width and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
        else:
            current_line.append(word)
            current_length += space_length + word_length

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)

    # Even simpler version using textwrap


def word_new_line_tag_simple(text, max_width=30):
    import textwrap
    if not text:
        return ""
    return '\n'.join(textwrap.wrap(text, width=max_width, break_long_words=False))

