from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from content_scorer import parse_for_main_content
import time

# Path to the Firefox profile
profile_path = 'C:\\Users\\xxxyyyy\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\7kzkf5tt.default'

# Path to the GeckoDriver executable
geckodriver_path = './downloads/geckodriver.exe'

# Path to the Firefox binary
firefox_binary_path = 'path to\\firefox.exe'

# Set up Firefox options
options = Options()
options.headless = True  # Run in headless mode
options.binary_location = firefox_binary_path  # Specify the Firefox binary location

# Load the Firefox profile
options.set_preference('profile', profile_path)

# Set up the service for GeckoDriver
service = Service(executable_path=geckodriver_path)

# Initialize the WebDriver with the profile
driver = webdriver.Firefox(options=options, service=service)

# URL of the web page you want to extract content from
url = 'https://'

# Open the page
driver.get(url)

# Wait for the page to fully load
WebDriverWait(driver, 30).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

# Authentication for JPMorgan Chase
# XPath to locate the <div> with role="button", class="idp", and containing specific text
xpath = '//div[@role="button" and contains(@class, "idp") and descendant::text()[contains(., "title")]]'

# Wait for the element to be present
button_div = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, xpath))
)

# Click the <div> with role="button"
button_div.click()

# Wait for the page to fully load
WebDriverWait(driver, 30).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

try:
    # Inject JavaScript to monitor network requests if not already injected
    driver.execute_script("""
      if (typeof window.pendingRequests === 'undefined') {
          window.pendingRequests = 0;
          // Wrap XMLHttpRequest to count active requests. This patch may not cover errors or aborts.
          (function(open, send) {
              XMLHttpRequest.prototype.open = function() {
                  // Add event listeners to know when a request starts/ends.
                  this.addEventListener('readystatechange', function() {
                      if (this.readyState === XMLHttpRequest.OPENED) {
                          window.pendingRequests++;
                      }
                      if (this.readyState === XMLHttpRequest.DONE) {
                          // Use a slight delay to account for cases where new requests might be chained.
                          setTimeout(function() {
                              window.pendingRequests = Math.max(window.pendingRequests - 1, 0);
                          }, 50);
                      }
                  }, false);
                  open.apply(this, arguments);
              };
              XMLHttpRequest.prototype.send = function() {
                  send.apply(this, arguments);
              };
          })(XMLHttpRequest.prototype.open, XMLHttpRequest.prototype.send);
          // Wrap fetch to count active requests.
          if (window.fetch) {
              const originalFetch = window.fetch;
              window.fetch = function() {
                  window.pendingRequests++;
                  return originalFetch.apply(this, arguments).finally(function() {
                      // Use a slight delay to handle chained requests smoothly.
                      setTimeout(function() {
                          window.pendingRequests = Math.max(window.pendingRequests - 1, 0);
                      }, 50);
                  });
              };
          }
      }
    """)

    def wait_for_network_idle(idle_time=2.0, timeout=30.0):
        """Wait until window.pendingRequests remains 0 for at least idle_time seconds."""
        end_time = time.time() + timeout
        idle_start = None

        while time.time() < end_time:
            pending = driver.execute_script("return window.pendingRequests")
            print(f"Pending requests: {pending}")  # Debug output for monitoring
            if pending == 0:
                if idle_start is None:
                    idle_start = time.time()
                elif time.time() - idle_start >= idle_time:
                    return True
            else:
                idle_start = None  # Reset if a new request comes in
            time.sleep(0.5)
        return False

    # Adjust idle_time to a longer period if needed (e.g., 2 seconds)
    if wait_for_network_idle(idle_time=2.0, timeout=30.0):
        print("Network is idle, page loading seems complete.")
    else:
        print("Timeout waiting for network to idle.")

    time.sleep(5)
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    if not iframe :
        driver.switch_to.frame(iframe)
    else:
        print("Iframe not found")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.dispatchEvent(new Event('resize'));")
    time.sleep(2)

    driver.execute_script("""
        window.observerTriggered = false;
        const observer = new MutationObserver(function(mutations) {
            window.observerTriggered = true;
        });
        observer.observe(document.body, { childList: true, subtree: true });
    """)

    # Wait a bit and then check if updates occurred
    time.sleep(5)
    triggered = driver.execute_script("return window.observerTriggered;")
    print("Mutations recorded: ", triggered)

    content = driver.execute_script("return document.querySelector('body').innerText;")
    print(content)
    driver.save_screenshot("screenshot.png")

finally:
    # Always quit the driver to free up resources
    driver.quit()

with open("page_source.html", "w", encoding="utf-8") as f:
    f.write(content)