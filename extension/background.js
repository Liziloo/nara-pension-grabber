console.log("Extension Background Script Loaded");

browser.action.onClicked.addListener(async (tab) => {
  console.log("Button clicked on tab:", tab.id);

  try {
    const results = await browser.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        console.log("Scraping page...");
        const naid = document.body.innerText.match(/\b\d{9}\b/)?.[0];
        const max = document
          .querySelector('input[aria-label="Enter Image number"]')
          ?.getAttribute("max");
        return { naid, max };
      },
    });

    const data = results[0].result;
    console.log("Scraped data:", data);

    if (data.naid) {
      console.log("Sending message to native host...");
      browser.runtime.sendNativeMessage("com.nara.pension.grabber", data);
    } else {
      console.warn("No NAID found on this page.");
    }
  } catch (err) {
    console.error("Extension Error:", err);
  }
});
