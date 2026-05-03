chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'collect') {
        fetch(`${API_BASE}/api/collect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: request.url,
                user_id: getUserId()
            })
        })
        .then(res => res.json())
        .then(data => sendResponse(data))
        .catch(err => sendResponse({ success: false, error: err.message }));
        return true;
    }
});

function getUserId() {
    let userId = localStorage.getItem('scribeai_user_id');
    if (!userId) {
        userId = 'user_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('scribeai_user_id', userId);
    }
    return userId;
}
