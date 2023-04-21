function detectLanguage(text) {
    const encoder = new TextEncoder();
    const dataView = encoder.encode(text);
    const decoder = new TextDecoder('utf-8', { fatal: true });
    const decodedText = decoder.decode(dataView);
    if (/[\u4e00-\u9fa5]/.test(decodedText) && /[a-zA-Z]/.test(decodedText)) {
        return 'mixed';
    } else if (/[\u4e00-\u9fa5]/.test(decodedText)) {
        return 'chinese';
    } else if (/[a-zA-Z]/.test(decodedText)) {
        return 'english';
    } else {
        return 'unknown';
    }
}

function detailsContentText(text) {
    let elementWidth = $('#details-content').width();
    let charWidth = 0;
    let complete = '';
    let divisor = 1.6;
    for (let char of text) {
        if (/[A-Z]/.test(char)) {
            // 大写英文字符
            charWidth += 24.75 / divisor;
        } else if (/[a-z]/.test(char)) {
            // 小写英文字符
            charWidth += 19.7 / divisor;
        } else if (/\s/.test(char)) {
            // 空格
            charWidth += 9.47 / divisor;
        } else if (/\d/.test(char)) {
            // 数字
            charWidth += 18.77 / divisor;
        } else if (/^[\u4e00-\u9fa5]$/.test(char)) {
            // 汉字
            charWidth += 32 / divisor;
        } else {
            // 其他
            charWidth += 32 / divisor;
        }
        if (charWidth > elementWidth) {
            complete += '...';
            break;
        }
        complete += char;
    }
    return complete;
}