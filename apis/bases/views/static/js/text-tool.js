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