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
    for (const url of apiEndpoints) {
      try {
        const response = await new Promise((resolve, reject) => {
          chrome.runtime.sendMessage({ action: "fetchIp", url }, response => {
            if (response.success) {
              resolve(response.data);
            } else {
              reject(new Error(response.error));
            }
          });
        });
        ipAddresses.push(`<div class="ip-row"><div class="ip-source">${new URL(url).hostname}</div><div class="ip-value">${response}</div></div>`);
      } catch (error) {
        console.error(`Error fetching IP from ${url}:`, error);
        ipAddresses.push(`<div class="ip-row"><div class="ip-source">${new URL(url).hostname}</div><div class="ip-value">${error.message}</div></div>`);
      }
    }
    ipAddressDiv.innerHTML = ipAddresses.join('');
  }

  // Get local IP from background script
  
  displayIpAddresses();
});