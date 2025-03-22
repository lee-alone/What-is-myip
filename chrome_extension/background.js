// 代理请求函数
async function proxyFetch(url) {
  try {
    const response = await fetch(url);
    const text = await response.text();
    if (url.startsWith('http://checkip.dyndns.org')) {
      const match = text.match(/Current IP Address: ([\d.]+)/);
      return match ? match[1] : text;
    }
    if (url.startsWith('https://api.my-ip.io')) {
      const data = JSON.parse(text);
      return `${data.ip} (${data.country.code})`;
    }
    if (url.startsWith('https://ipinfo.io')) {
      const data = JSON.parse(text);
      return `${data.ip} (${data.country})`;
    }
    if (url.startsWith('http://api.myip.com')) {
      const data = JSON.parse(text);
      if (data && data.ip && data.cc) {
        return `${data.ip} (${data.cc})`;
      }
      return '查询失败';
    }
    return text;
  } catch (error) {
    throw new Error(`请求失败: ${error.message}`);
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getLocalIp") {
    getLocalIPs()
      .then(localIp => sendResponse(localIp))
      .catch(error => {
        console.error('获取本地IP失败:', error);
        sendResponse('获取失败');
      });
    return true;
  } else if (request.action === "fetchIp") {
    proxyFetch(request.url)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});