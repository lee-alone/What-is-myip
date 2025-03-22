document.addEventListener('DOMContentLoaded', () => {
  const ipAddressDiv = document.getElementById('ipAddress');
  const apiEndpoints = [
    'https://api.my-ip.io/v2/ip.json',
    'https://ipinfo.io/json',
    'http://checkip.dyndns.org',
    'https://ifconfig.me/ip',
    'https://ipecho.net/plain',
    'https://api.myip.com'
  ];

  async function displayIpAddresses() {
    ipAddressDiv.innerHTML = '<span class="loading">正在加载...</span>';
    let ipAddresses = [];
    const promises = apiEndpoints.map(url => {
      return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ action: "fetchIp", url }, response => {
          if (response.success) {
            resolve({ url, data: response.data });
          } else {
            reject({ url, error: new Error(response.error) });
          }
        });
      });
    });

    const results = await Promise.allSettled(promises);

    ipAddresses = results.map(result => {
      if (result.status === 'fulfilled') {
        const { url, data } = result.value;
        return `<div class="ip-row"><div class="ip-source">${new URL(url).hostname}</div><div class="ip-value">${data}</div></div>`;
      } else {
        const { url, error } = result.reason;
        console.error(`Error fetching IP from ${url}:`, error);
        return `<div class="ip-row"><div class="ip-source">${new URL(url).hostname}</div><div class="ip-value">${error.message}</div></div>`;
      }
    });
    ipAddressDiv.innerHTML = ipAddresses.join('');
  }

  // Get local IP from background script
  
  displayIpAddresses();
});