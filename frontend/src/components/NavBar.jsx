function NavBar() {
  return (
    <>
      {/* implementing the navigation bar*/}
      <header className="site-header">
        <nav className="navbar navbar-expand-md navbar-dark bg-success fixed-top">
          <div className="container">
            {/* The Lab button (Welcome screen)*/}
            <div className="navbar-brand-wrapper d-flex align-items-center">
              <a className="navbar-brand mr-4" href="/">
                The Lab
              </a>
            </div>

            {/* Navbar toggler */}
            <button
              className="navbar-toggler"
              type="button"
              data-toggle="collapse"
              data-target="#navbarToggle"
              aria-controls="navbarToggle"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon"></span>
            </button>

            {/* Navbar Content */}
            <div className="collapse navbar-collapse" id="navbarToggle">
              {/* Nav Links */}
              <div className="navbar-nav mr-auto">
                <a className="nav-item nav-link" href="#">
                  Coaches
                </a>
                <a className="nav-item nav-link" href="#">
                  Events
                </a>
                <a className="nav-item nav-link" href="#">
                  Drills
                </a>
                <a className="nav-item nav-link" href="#">
                  Community
                </a>
              </div>
            </div>

            {/* Logo Image */}
            <div className="navbar-brand mx-auto">
              <div style={{ marginRight: "200px" }}>
                <a
                  href="#"
                  className="logo-wrapper d-flex justify-content-center"
                >
                  <img
                    src="./logo_white_png.png"
                    alt="Button Image"
                    width="50"
                    height="50"
                  />
                </a>
              </div>
            </div>
            {/* NavBar Right Side */}
            <div className="navbar-nav">
              {/* 
                {% if request.user.is_authenticated %}
                  Check if User's Profile is a Coach 
                  {% if profile.coach %}
                    <a className="nav-item nav-link" href="{% url 'page_viewing' pk=request.user.pk %}">Page</a>
                  {% endif %}
                  <a className="nav-item nav-link" href="{% url 'home' %}">Home</a>
                  <a className="nav-item nav-link" href="{% url 'alerts' %}">Alerts</a>
                {% else %}
                */}
              <a className="nav-item nav-link" href="/">
                Log In
              </a>
              <a className="nav-item nav-link" href="/">
                Create a Profile
              </a>
              {/* {% endif %} */}
            </div>
          </div>
        </nav>
      </header>
      {/*
              <div className="col-md-8">
                {/* Printing out any messages that might appear 
                {% if messages %}
                  {% for message in messages %}
                    <div className = "alert alert-{{ message.tags }}">{/* Bootstrap classes for alerts (messages in Bootstrap have the same classes as the messages in python)
                      {{ message }}
                    </div>
                  {% endfor %}
                {% endif %}
                {/* Filling in the rest of the screen 
                  {% block content %}
                  {% endblock %}
              */}
    </>
  );
}

export default NavBar;
