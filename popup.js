const API_BASE = 'http://localhost:8000';

const statusEl = document.getElementById('status');
const titleEl = document.getElementById('pageTitle');
const urlEl = document.getElementById('pageUrl');
const resultEl = document.getElementById('result');
const summaryEl = document.getElementById('resultSummary');
const tagsEl = document.getElementById('resultTags');
const collectBtn = document.getElementById('collectBtn');

let currentPage = {
    url: '',
    title: ''
};

function getUserId() {
    let userId = localStorage.getItem('scribeai_user_id');
    if (!userId) {
        userId = 'user_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('scribeai_user_id', userId);
    }
    return userId;
}

function showStatus(message, type) {
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    statusEl.style.display = 'block';
}

function hideStatus() {
    statusEl.style.display = 'none';
}

async function collect() {
    if (!currentPage.url) return;

    collectBtn.disabled = true;
    collectBtn.textContent = '分析中...';
    showStatus('正在分析页面内容...', 'loading');

    try {
        const response = await fetch(`${API_BASE}/api/collect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: currentPage.url,
                user_id: getUserId()
            })
        });

        const result = await response.json();

        if (result.success) {
            showStatus('收藏成功！', 'success');

            summaryEl.textContent = result.data.summary || '无总结';
            tagsEl.innerHTML = (result.data.tags || []).map(
                tag => `<span class="tag">${tag}</span>`
            ).join('');

            resultEl.style.display = 'block';
            collectBtn.textContent = '已收藏';
        } else {
            throw new Error(result.detail || '收藏失败');
        }
    } catch (error) {
        showStatus(`收藏失败: ${error.message}`, 'error');
        collectBtn.disabled = false;
        collectBtn.textContent = '重试';
    }
}

async function checkIfCollected() {
    try {
        const response = await fetch(
            `${API_BASE}/api/contents?user_id=${getUserId()}`
        );
        const result = await response.json();

        if (result.success) {
            const found = result.data.contents?.find(
                item => item.url === currentPage.url
            );

            if (found) {
                collectBtn.textContent = '已收藏';
                collectBtn.disabled = true;

                summaryEl.textContent = found.summary || '无总结';
                tagsEl.innerHTML = (found.tags || []).map(
                    tag => `<span class="tag">${tag}</span>`
                ).join('');
                resultEl.style.display = 'block';
            } else {
                collectBtn.disabled = false;
                collectBtn.textContent = '一键收藏';
            }
        }
    } catch (e) {
        collectBtn.disabled = false;
        collectBtn.textContent = '一键收藏';
    }
}

collectBtn.addEventListener('click', collect);

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
        currentPage.url = tabs[0].url;
        currentPage.title = tabs[0].title || '无标题';

        titleEl.textContent = currentPage.title;
        urlEl.textContent = currentPage.url;

        checkIfCollected();
    }
});
