browser.action.onClicked.addListener(async (tab) => {
  console.log("Starting targeted scrape...");

  try {
    const results = await browser.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        console.log("Searching specifically for the NAID...");

        // Target the shared viewer references section from your screenshot
        const infoPanel = document.querySelector(
          '#shared-image-viewer-references-section, aside[aria-label="Information"]'
        );

        if (!infoPanel) {
          console.error("Info panel not found in DOM.");
          return { naid: null, max: "1" };
        }

        // Instead of innerText (which hangs), let's look at all div text content
        const allDivs = infoPanel.querySelectorAll("div");
        let naid = null;

        for (let div of allDivs) {
          // Check if the div content is EXACTLY or contains a 9-digit number
          const text = div.textContent.trim();
          if (/^\d{9}$/.test(text)) {
            naid = text;
            console.log("Found NAID in div:", naid);
            break;
          }
        }

        const msgInput = document.querySelector(
          'input[aria-label="Enter Image number"]'
        );
        const max = msgInput ? msgInput.getAttribute("max") : "1";

        return { naid, max };
      },
    });

    const data = results[0].result;

    if (data.naid) {
      console.log("Found NAID:", data.naid, "sending to Python...");
      browser.runtime.sendNativeMessage("com.nara.pension.grabber", data);
    } else {
      console.error(
        "Scraper failed: Could not find 9-digit ID in the info panel."
      );
    }
  } catch (err) {
    console.error("Execution error:", err);
  }
});
