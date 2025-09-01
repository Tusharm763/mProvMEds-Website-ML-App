// Dropdown functionality
function toggleDropdown() {
  const dropdown = document.getElementById("dropdownMenu");
  const arrow = document.querySelector(".dropdown-arrow");
  dropdown.classList.toggle("active");
  arrow.style.transform = dropdown.classList.contains("active")
    ? "rotate(180deg)"
    : "rotate(0deg)";
}

// Close dropdown when clicking outside
document.addEventListener("click", function (event) {
  const dropdown = document.getElementById("dropdownMenu");
  const userButton = document.querySelector(".user-button");

  if (userButton && !userButton.contains(event.target)) {
    dropdown.classList.remove("active");
    const arrow = document.querySelector(".dropdown-arrow");
    if (arrow) {
      arrow.style.transform = "rotate(0deg)";
    }
  }
});
// Smooth scroll to top
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

// Add scroll to top button
window.addEventListener("scroll", function () {
  const scrollBtn = document.getElementById("scrollToTop");
  if (!scrollBtn) {
    const btn = document.createElement("button");
    btn.id = "scrollToTop";
    btn.innerHTML = "&uarr; Scroll to Top";
    btn.style.cssText = `
                    position: fixed;
                    font-size: 1rem;
                    bottom: 2rem;
                    right: 2rem;
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding-left: 1rem;
                    padding-right:1rem;
                    padding-top: 1rem;
                    padding-bottom: 1rem;

                    border-radius: 30px;
                    //width: 100px;
                    //height: 50px;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                    z-index: 1000;
                    display: none;
                `;
    btn.onclick = scrollToTop;
    document.body.appendChild(btn);
  }

  const scrollTopBtn = document.getElementById("scrollToTop");
  if (window.pageYOffset > 300) {
    scrollTopBtn.style.display = "block";
  } else {
    scrollTopBtn.style.display = "none";
  }
});

// Auto-hide flash messages
setTimeout(function () {
  const flashMessages = document.querySelectorAll(".flash-message");
  flashMessages.forEach(function (message) {
    message.style.opacity = "0";
    setTimeout(function () {
      message.remove();
    }, 300);
  });
}, 5000);

// Prevent duplicate symptom selection
function validateSymptoms() {
  const inputs = document.querySelectorAll('input[list="Sympto_list"]');
  const values = Array.from(inputs)
    .map((input) => input.value.trim())
    .filter((value) => value);
  const uniqueValues = [...new Set(values)];

  if (values.length !== uniqueValues.length) {
    alert("Please avoid selecting duplicate symptoms.");
    return false;
  }
  return true;
}

// Enhanced print functionality
function printResults() {
  const printContent = document.querySelector(".result-container").innerHTML;
  const printWindow = window.open("", "", "height=600,width=800");
  printWindow.document.write(`
                <html>
                <head>
                    <title>Health Prediction Results</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .disease { background: #f0f9ff; padding: 10px; margin: 10px 0; border-radius: 5px; }
                        .symptom-tag { background: #fef3c7; padding: 5px; margin: 2px; border-radius: 15px; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <h1>Health Prediction Results</h1>
                    <p>Generated on: ${new Date().toLocaleString()}</p>
                    ${printContent}
                </body>
                </html>
            `);
  printWindow.document.close();
  printWindow.print();
}

//
//// Clear prediction history (client-side only for demo)
//function clearHistory() {
//  if (
//    confirm(
//      "Are you sure you want to clear your prediction history? This action cannot be undone."
//    )
//  ) {
//    alert(
//      "Note: This is a demo. In a real application, this would clear your history from the server."
//    );
//    // In a real app, you would make an AJAX call to delete the user's predictions
//    // fetch('/clear-predictions', {method: 'POST'})...
//  }
//}

// Search/filter functionality
function createSearchFilter() {
  const searchContainer = document.createElement("div");
  searchContainer.innerHTML = `
                <div style="margin-bottom: 2rem; text-align: center;">
                    <input type="text" id="searchInput" placeholder="Search predictions by symptoms or diseases..."
                           style="width: 100%; max-width: 400px; padding: 0.75rem 1rem; border: 2px solid var(--border); border-radius: var(--border-radius-sm); font-size: 1rem;">
                </div>
            `;

  const container = document.querySelector(".predictions-container");
  const firstCard = document.querySelector(".prediction-card");
  if (firstCard) {
    container.insertBefore(searchContainer, firstCard);

    document
      .getElementById("searchInput")
      .addEventListener("input", function (e) {
        const searchTerm = e.target.value.toLowerCase();
        const cards = document.querySelectorAll(".prediction-card");

        cards.forEach((card) => {
          const text = card.textContent.toLowerCase();
          if (text.includes(searchTerm)) {
            card.style.display = "block";
          } else {
            card.style.display = "none";
          }
        });
      });
  }
}

// Add search if there are predictions
if (document.querySelectorAll(".prediction-card").length > 3) {
  createSearchFilter();
}

// Form validation
function validateContactForm() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const contactType = document.getElementById("contact_type").value;
  const query = document.getElementById("query").value.trim();

  if (!name || !email || !contactType || !query) {
    alert("Please fill in all required fields.");
    return false;
  }

  if (query.length < 10) {
    alert("Please provide a more detailed message (at least 10 characters).");
    return false;
  }

  // Add loading state
  const submitBtn = document.querySelector('button[type="submit"]');
  submitBtn.innerHTML = "⏳ Sending...";
  submitBtn.disabled = true;

  return true;
}

// Auto-hide flash messages
setTimeout(function () {
  const flashMessages = document.querySelectorAll(".flash-message");
  flashMessages.forEach(function (message) {
    message.style.opacity = "0";
    setTimeout(function () {
      message.remove();
    }, 300);
  });
}, 5000);

//        // Show priority field for reports and support requests
//        document.getElementById('contact_type').addEventListener('change', function() {
//            const priorityGroup = document.getElementById('priority-group');
//            const value = this.value;
//
//            if (value === 'report' || value === 'support') {
//                priorityGroup.style.display = 'block';
//            } else {
//                priorityGroup.style.display = 'none';
//            }
//        });

function isMobileDevice() {
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());
            const isSmallScreen = window.matchMedia("(max-width: 768px)").matches;
            return isMobile || isSmallScreen;
        }

        window.onload = function() {
            const messageElement = document.getElementById('mobileMessage');

            const messageElement1 = document.getElementById('nb');
            const messageElement2 = document.getElementById('cmc');
            const messageElement3 = document.getElementById('sf');
            if (isMobileDevice()) {
                messageElement.style.display = 'block';
                messageElement1.style.display = 'none';
                messageElement2.style.display = 'none';
                messageElement3.style.display = 'none';
            }
        };