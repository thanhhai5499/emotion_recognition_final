/**
 * Emotion Recognition Web App - Main JavaScript
 * Xử lý các tương tác của người dùng và cập nhật giao diện
 */

document.addEventListener("DOMContentLoaded", function () {
  // DOM Elements
  const comPortSelect = document.getElementById("com-port");
  const arduinoStatus = document.getElementById("arduino-status");
  const emotionValue = document.getElementById("emotion-value");
  const warningValue = document.getElementById("warning-value");
  const heartrateValue = document.getElementById("heartrate-value");
  const lastUpdate = document.getElementById("last-update");
  const connectBtn = document.getElementById("btn-connect");
  const disconnectBtn = document.getElementById("btn-disconnect");
  const exitBtn = document.getElementById("btn-exit");
  const logoutBtn = document.getElementById("btn-logout");
  const messageBox = document.getElementById("message-box");
  const videoFeeds = document.querySelectorAll(".video-container img");

  // Check if user is authenticated
  function checkAuthentication() {
    fetch("/api/check_authentication")
      .then((response) => response.json())
      .then((data) => {
        if (!data.authenticated) {
          // Redirect to login page if not authenticated
          window.location.href = "/login";
        }
      })
      .catch((error) => {
        console.error("Error checking authentication:", error);
      });
  }

  // Add loading class to video containers
  document.querySelectorAll(".video-container").forEach((container) => {
    container.classList.add("loading");
  });

  // Toast notification system
  const toastContainer = document.createElement("div");
  toastContainer.className = "toast-container";
  document.body.appendChild(toastContainer);

  function showToast(message, type = "info", duration = 3000) {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    // Progress bar
    const progressBar = document.createElement("div");
    progressBar.className = "progress";
    const progressInner = document.createElement("div");
    progressInner.className = "progress-bar";
    progressBar.appendChild(progressInner);
    toast.appendChild(progressBar);

    toastContainer.appendChild(toast);

    // Show toast
    setTimeout(() => {
      toast.classList.add("show");
      progressInner.style.width = "100%";
      progressInner.style.transitionDuration = `${duration}ms`;
    }, 10);

    // Hide toast after duration
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => {
        toastContainer.removeChild(toast);
      }, 300);
    }, duration);
  }

  // Add fade-in animation to the page
  document.body.classList.add("fade-in");

  // Fetch COM ports
  function fetchComPorts() {
    fetch("/api/com_ports")
      .then((response) => response.json())
      .then((data) => {
        comPortSelect.innerHTML = '<option value="">Chọn cổng COM</option>';

        if (data.length === 0) {
          const option = document.createElement("option");
          option.value = "";
          option.textContent = "Không tìm thấy cổng COM nào";
          option.disabled = true;
          comPortSelect.appendChild(option);
          showToast("Không tìm thấy cổng COM nào", "warning");
        } else {
          data.forEach((port) => {
            const option = document.createElement("option");
            option.value = port.device;
            option.textContent = `${port.device} - ${port.description}`;
            comPortSelect.appendChild(option);
          });
          showToast(`Đã tìm thấy ${data.length} cổng COM`, "success");
        }
      })
      .catch((error) => {
        console.error("Error fetching COM ports:", error);
        showToast("Lỗi khi lấy danh sách cổng COM", "error");
      });
  }

  // Update status
  function updateStatus() {
    fetch("/api/status")
      .then((response) => response.json())
      .then((data) => {
        // Remove loading class from video containers once we get data
        document
          .querySelectorAll(".video-container.loading")
          .forEach((container) => {
            container.classList.remove("loading");
          });

        // Update emotion status
        updateElement(
          emotionValue,
          data.emotion.emotion,
          data.emotion.emotion_color
        );

        // Update warning status
        updateElement(
          warningValue,
          data.emotion.rest_message || "Không có",
          data.emotion.rest_color
        );

        // Update heartrate
        updateElement(
          heartrateValue,
          data.heartrate.value,
          data.heartrate.color
        );

        // Update Arduino status
        updateElement(arduinoStatus, data.arduino.message, data.arduino.color);

        // Update last update time
        lastUpdate.textContent = data.timestamp;

        // Enable/disable buttons based on Arduino connection status
        disconnectBtn.disabled = !data.arduino.connected;
        connectBtn.disabled = data.arduino.connected;

        if (!data.arduino.connected) {
          disconnectBtn.classList.add("opacity-50", "cursor-not-allowed");
          connectBtn.classList.remove("opacity-50", "cursor-not-allowed");
        } else {
          disconnectBtn.classList.remove("opacity-50", "cursor-not-allowed");
          connectBtn.classList.add("opacity-50", "cursor-not-allowed");
        }
      })
      .catch((error) => {
        console.error("Error updating status:", error);
      });
  }

  // Helper to update an element's text and color with animation
  function updateElement(element, newText, newColor) {
    if (!element) return;

    if (element.textContent !== newText) {
      // Add a subtle highlight effect when value changes
      element.classList.add("pulse");
      setTimeout(() => {
        element.classList.remove("pulse");
      }, 1000);
    }

    element.textContent = newText;
    element.style.color = newColor;
  }

  // Connect Arduino
  function connectArduino() {
    const port = comPortSelect.value;

    if (!port) {
      showToast("Vui lòng chọn cổng COM!", "warning");
      return;
    }

    // Show loading indicator
    connectBtn.innerHTML =
      '<span class="animate-spin inline-block mr-2">↻</span> Đang kết nối...';
    connectBtn.disabled = true;

    fetch("/api/connect_arduino", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ port }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Reset button
        connectBtn.innerHTML = "Xác Nhận";
        connectBtn.disabled = false;

        if (data.success) {
          showToast(`Đã kết nối thành công đến ${port}`, "success");
          updateStatus(); // Update status immediately
        } else {
          showToast(`Lỗi kết nối: ${data.message}`, "error");
        }
      })
      .catch((error) => {
        // Reset button
        connectBtn.innerHTML = "Xác Nhận";
        connectBtn.disabled = false;

        console.error("Error connecting Arduino:", error);
        showToast("Lỗi kết nối Arduino!", "error");
      });
  }

  // Disconnect Arduino
  function disconnectArduino() {
    // Show loading indicator
    disconnectBtn.innerHTML =
      '<span class="animate-spin inline-block mr-2">↻</span> Đang ngắt kết nối...';
    disconnectBtn.disabled = true;

    fetch("/api/disconnect_arduino", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        // Reset button
        disconnectBtn.innerHTML = "Ngắt kết nối";
        disconnectBtn.disabled = false;

        if (data.success) {
          showToast("Đã ngắt kết nối Arduino thành công", "success");
          updateStatus(); // Update status immediately
        }
      })
      .catch((error) => {
        // Reset button
        disconnectBtn.innerHTML = "Ngắt kết nối";
        disconnectBtn.disabled = false;

        console.error("Error disconnecting Arduino:", error);
        showToast("Lỗi khi ngắt kết nối Arduino", "error");
      });
  }

  // Logout user
  function logoutUser() {
    if (confirm("Bạn có chắc muốn đăng xuất?")) {
      fetch("/api/logout", {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            showToast("Đăng xuất thành công", "success");
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 1000);
          } else {
            showToast("Lỗi khi đăng xuất", "error");
          }
        })
        .catch((error) => {
          console.error("Error logging out:", error);
          showToast("Lỗi khi đăng xuất", "error");
        });
    }
  }

  // Exit application
  function exitApplication() {
    if (confirm("Bạn có chắc muốn thoát ứng dụng?")) {
      // Show loading animation
      document.body.innerHTML = `
                <div class="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-gray-800 bg-opacity-75 z-50">
                    <div class="text-center p-10 bg-white rounded-lg shadow-lg">
                        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
                        <h2 class="text-xl font-bold mb-2">Đang tắt ứng dụng...</h2>
                        <p class="text-gray-600">Vui lòng đợi trong giây lát</p>
                    </div>
                </div>`;

      fetch("/api/shutdown", {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          document.body.innerHTML = `
                    <div class="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-gray-800 bg-opacity-75 z-50">
                        <div class="text-center p-10 bg-white rounded-lg shadow-lg">
                            <div class="text-6xl text-success mb-4">✓</div>
                            <h2 class="text-xl font-bold mb-2">Ứng dụng đã tắt thành công</h2>
                            <p class="text-gray-600">Bạn có thể đóng cửa sổ này bây giờ</p>
                        </div>
                    </div>`;
        })
        .catch((error) => {
          console.error("Error shutting down application:", error);
          document.body.innerHTML = `
                    <div class="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-gray-800 bg-opacity-75 z-50">
                        <div class="text-center p-10 bg-white rounded-lg shadow-lg">
                            <div class="text-6xl text-danger mb-4">✗</div>
                            <h2 class="text-xl font-bold mb-2">Lỗi khi tắt ứng dụng</h2>
                            <p class="text-gray-600">Vui lòng thử lại sau</p>
                        </div>
                    </div>`;
        });
    }
  }

  // Setup status interval
  function setupStatusInterval() {
    // Initial update
    updateStatus();
    fetchComPorts();

    // Setup intervals
    setInterval(updateStatus, 1000); // Update status every second
    setInterval(fetchComPorts, 30000); // Refresh COM ports every 30 seconds
  }

  // Setup event listeners
  function setupEventListeners() {
    if (connectBtn) {
      connectBtn.addEventListener("click", connectArduino);
    }

    if (disconnectBtn) {
      disconnectBtn.addEventListener("click", disconnectArduino);
    }

    if (exitBtn) {
      exitBtn.addEventListener("click", exitApplication);
    }

    if (logoutBtn) {
      logoutBtn.addEventListener("click", logoutUser);
    }
  }

  // Check authentication on page load
  checkAuthentication();

  // Initialize the application
  setupStatusInterval();
  setupEventListeners();

  // Handle video feed errors
  videoFeeds.forEach((feed) => {
    feed.onerror = function () {
      const container = feed.closest(".video-container");
      if (container) {
        container.innerHTML = `
                    <div class="w-full h-full flex items-center justify-center bg-gray-800 text-white">
                        <div class="text-center">
                            <svg class="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <p class="mt-2">Không thể kết nối camera</p>
                            <button class="mt-2 px-3 py-1 bg-primary text-white text-sm rounded" 
                                    onclick="location.reload()">Thử lại</button>
                        </div>
                    </div>
                `;
      }
    };

    feed.onload = function () {
      const container = feed.closest(".video-container");
      if (container) {
        container.classList.remove("loading");
      }
    };
  });

  // Refresh COM ports
  document.addEventListener("keydown", function (event) {
    // Press F5 to refresh COM ports
    if (event.key === "F5") {
      event.preventDefault();
      fetchComPorts();
    }
  });

  // Add tooltip for refresh
  const selectWrapper = comPortSelect.closest(".relative");
  if (selectWrapper) {
    const refreshBtn = document.createElement("span");
    refreshBtn.className =
      "absolute right-8 top-1/2 transform -translate-y-1/2 cursor-pointer text-primary tooltip";
    refreshBtn.innerHTML = "↻";
    refreshBtn.setAttribute("data-tooltip", "Làm mới danh sách cổng COM (F5)");
    refreshBtn.addEventListener("click", fetchComPorts);
    selectWrapper.appendChild(refreshBtn);
  }
});
