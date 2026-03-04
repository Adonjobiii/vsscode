import os
import pymongo
from flask import Flask, request, render_template_string, jsonify

# Connect to MongoDB
# IMPORTANT: Replace the placeholder below with your actual MongoDB connection string.
# Example: "mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority"
MONGO_URI = "YOUR_MONGODB_CONNECTION_STRING"

app = Flask(__name__)

# The HTML content as a multi-line string.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>path=wise - Sign Up</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .slide {
      position: absolute;
      inset: 0;
      opacity: 0;
      transition: opacity 1s ease-in-out;
    }
    .active-slide {
      opacity: 1;
    }
  </style>
</head>
<body class="h-screen w-screen bg-gray-800">
  <div class="flex h-screen">
    
    <!-- Left Form Section -->
    <div class="w-1/2 flex items-center justify-center bg-gray-700">
      <div class="w-3/4 max-w-md">
        <h1 class="text-4xl font-bold text-center text-black">WELCOME</h1>
        <p class="text-black text-center mt-2">Start your journey with us </p>

        <!-- Progress Bar -->
        <div class="mt-6">
          <p class="text-sm font-medium text-black">Step 1 of 2 <span class="float-right text-gray-900">50% complete</span></p>
          <div class="w-full bg-gray-600 rounded-full h-2 mt-2">
            <div class="bg-green-500 h-2 rounded-full" style="width: 50%"></div>
          </div>
        </div>

        <!-- Form -->
        <div class="mt-8">
          <h2 class="text-lg font-semibold text-center text-black">Basic Information</h2>
          <p class="text-black text-center">Tell us about yourself</p>

          <button class="w-full flex items-center justify-center border border-gray-500 rounded-lg py-2 mt-6 hover:bg-gray-600 text-black">
              Continue with Google
          </button>
          <button class="w-full flex items-center justify-center border border-gray-500 rounded-lg py-2 mt-3 hover:bg-gray-600 text-black">
              Continue with Apple
          </button>

          <div class="flex items-center my-6">
            <hr class="flex-grow border-gray-500">
            <span class="px-2 text-gray-700 text-sm">or continue with email</span>
            <hr class="flex-grow border-gray-500">
          </div>

          <form id="signup-form">
            <div class="grid grid-cols-2 gap-4">
              <input type="text" id="first-name" name="first_name" placeholder="First Name" class="bg-gray-600 text-black border border-gray-500 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500">
              <input type="text" id="last-name" name="last_name" placeholder="Last Name" class="bg-gray-600 text-black border border-gray-500 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500">
            </div>
            <input type="email" id="email" name="email" placeholder="Email Address" class="w-full bg-gray-600 text-black border border-gray-500 rounded-lg px-4 py-2 mt-4 focus:ring-2 focus:ring-green-500">

            <button type="submit" class="w-full bg-green-600 text-white rounded-lg py-2 mt-6 hover:bg-green-700 flex items-center justify-center">
              Continue →
            </button>
          </form>
          
          <div id="message-container" class="mt-4 text-center"></div>

          <p class="text-xs text-gray-700 mt-4 text-center">
            By continuing, you agree to our <a href="#" class="text-green-700">Terms of Service</a> and <a href="#" class="text-green-700">Privacy Policy</a>.
          </p>
          <p class="text-sm text-center mt-4 text-black">
            Already have an account? <a href="#" class="text-green-700 font-medium">Sign in</a>
          </p>
        </div>
      </div>
    </div>

    <!-- Right Slideshow Section -->
    <div class="w-1/2 relative overflow-hidden h-screen">
      <div class="slide active-slide">
        <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80" class="w-full h-full object-cover">
        <div class="absolute inset-0 bg-black bg-opacity-50 flex flex-col justify-end p-10">
          <h2 class="text-green-400 text-3xl font-bold">Choose Your Future</h2>
          <p class="text-gray-200 mt-2">Bring your dream to life and know your passion.</p>
        </div>
      </div>

      <div class="slide">
        <img src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=80" class="w-full h-full object-cover">
        <div class="absolute inset-0 bg-black bg-opacity-50 flex flex-col justify-end p-10">
          <h2 class="text-green-400 text-3xl font-bold">Boost Productivity</h2>
          <p class="text-gray-200 mt-2">Achieve more with tools designed to optimize workflow and efficiency.</p>
        </div>
      </div>

      <div class="slide">
        <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80" class="w-full h-full object-cover">
        <div class="absolute inset-0 bg-black bg-opacity-50 flex flex-col justify-end p-10">
          <h2 class="text-green-400 text-3xl font-bold">Innovate Together</h2>
          <p class="text-gray-200 mt-2">Empower your team to create, collaborate, and inspire innovation.</p>
        </div>
      </div>
    </div>

  </div>

  <!-- Slideshow Script -->
  <script>
    let slides = document.querySelectorAll(".slide");
    let index = 0;

    function showSlide() {
      slides.forEach((slide, i) => {
        slide.classList.remove("active-slide");
        if (i === index) slide.classList.add("active-slide");
      });
      index = (index + 1) % slides.length;
    }

    setInterval(showSlide, 4000);

    const form = document.getElementById('signup-form');
    const messageContainer = document.getElementById('message-container');

    form.addEventListener('submit', async (event) => {
      event.preventDefault(); // Prevent the default form submission

      // Get form data
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());

      messageContainer.textContent = "Submitting...";
      messageContainer.style.color = "white";

      try {
        const response = await fetch('/signup', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
          messageContainer.textContent = result.message;
          messageContainer.style.color = "green";
          // Redirect to the next page after a delay
          setTimeout(() => {
            window.location.href = "hobbies.html";
          }, 2000); // Redirect after 2 seconds
        } else {
          messageContainer.textContent = result.error;
          messageContainer.style.color = "red";
        }
      } catch (error) {
        console.error('Error:', error);
        messageContainer.textContent = 'An error occurred. Please try again.';
        messageContainer.style.color = "red";
      }
    });
  </script>
</body>
</html>
"""

# The database connection and routes will only be created if a URI is provided.
if MONGO_URI != "YOUR_MONGODB_CONNECTION_STRING":
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client.get_database()
        users_collection = db.users
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        users_collection = None
else:
    print("Warning: MONGO_URI not set. Data will not be saved to MongoDB.")
    users_collection = None


@app.route('/')
def serve_form():
    """
    Renders the HTML form from the string template.
    """
    return render_template_string(HTML_TEMPLATE)

@app.route('/signup', methods=['POST'])
def signup():
    """
    Handles the form submission and saves the data to MongoDB.
    """
    if not users_collection:
        return jsonify({"error": "Database connection not available. Data could not be saved."}), 503

    try:
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')

        if not all([first_name, last_name, email]):
            return jsonify({"error": "All fields are required."}), 400

        # Insert the new user data into the 'users' collection
        users_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        })

        return jsonify({"message": "User registered successfully!"}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    # Flask will automatically use the PORT environment variable if set
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
