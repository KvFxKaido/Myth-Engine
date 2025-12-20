export const sendMessage = async (modelId, messages) => {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelId, messages }),
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Request failed');
    }

    const data = await response.json();
    return data.content;
};

export const getKeyStatus = async () => {
    const response = await fetch('/api/keys/status');
    if (!response.ok) throw new Error('Failed to fetch key status');
    return await response.json();
};

export const setKeys = async (keys) => {
    const response = await fetch('/api/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keys),
    });
    if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to save keys');
    }
    return await response.json();
};
