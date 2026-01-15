browser.action.onClicked.addListener(async (tab) => {
  try {
    const results = await browser.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        /* Scrape the 9-digit NAID and the 'max' attribute from the page input */
        const naid = document.body.innerText.match(/\b\d{9}\b/)?.[0];
        const max = document
          .querySelector('input[aria-label="Enter Image number"]')
          ?.getAttribute("max");
        return { naid, max };
      },
    });

    const data = results[0].result;
    if (data.naid) {
      /* This sends the data directly to nara_bridge.py via the JSON manifest */
      browser.runtime.sendNativeMessage("com.nara.pension.grabber", data);
    }
  } catch (err) {
    console.error("Failed to scrape or send:", err);
  }
});
