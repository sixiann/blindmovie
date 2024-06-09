const exampleMovies = [
  {
    link: "https://www.themoviedb.org/movie/299534-avengers-endgame?language=en-US",
    img: "https://lumiere-a.akamaihd.net/v1/images/p_avengersendgame_19751_e14a0104.jpeg",
    description:
      "Surviving heroes unite, rising from ruins to restore universal order",
  },
  {
    link: "https://www.themoviedb.org/movie/872585-oppenheimer?language=en-US",
    img: "https://m.media-amazon.com/images/M/MV5BMDBmYTZjNjUtN2M1MS00MTQ2LTk2ODgtNzc2M2QyZGE5NTVjXkEyXkFqcGdeQXVyNzAwMjU2MTY@._V1_.jpg",
    description:
      "Cillian Murphy and Emily Blunt depict the tumultuous journey of atomic bomb creator, J. Robert Oppenheimer.",
  },
  {
    link: "https://www.themoviedb.org/movie/346698-barbie?language=en-US",
    img: "https://i.ebayimg.com/images/g/1EcAAOSwa-9klig5/s-l1600.jpg",
    description: "Fantasy world, motherhood, satire, patriarchy",
  },
  {
    link: "https://www.themoviedb.org/movie/146?language=en-US",
    img: "https://m.media-amazon.com/images/M/MV5BNDdhMzMxOTctNDMyNS00NTZmLTljNWEtNTc4MDBmZTYxY2NmXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
    description:
      "Martial arts adventure unfolds in a whirlwind of love and secrets.",
  },
];

// Function to toggle containers
function toggleContainers() {
  var firstContainer = $("#first-container");
  var contentContainer = $("#content-container");

  firstContainer.hide(); // Hide the first container
  contentContainer.show(); // Show the content container
}

//function to get the blind date descriptions
function getMovies(mainstream) {
  $("#content-container").hide();
  $("#movies-container").hide();
  $("#loading-overlay").show();

  $.ajax({
    url: "/generate_descriptions?mainstream=" + mainstream,
    type: "GET",
    success: function (response) {
      var descriptions = response.blind_descriptions;
      var links = response.links;
      $("#content-container").hide();
      $("#loading-overlay").hide();
      $("#movies-container").show();

      if (
        descriptions &&
        descriptions.length > 0 &&
        links &&
        links.length > 0
      ) {
        $("#blind-date-movies").empty(); // Clear existing content

        for (var i = 0; i < descriptions.length; i++) {
          var html = 
          `<div class="mr-3">
                <a href="${links[i]}" target="_blank">
                    <div class="book">
                        <div class="tooltip">
                            <p>🍿click to reveal🍿</p>
                        </div>
                        <img src="https://t4.ftcdn.net/jpg/05/36/94/71/360_F_536947179_8TFyEQV04BmYEWud21q3Znq4jZBlz9qA.jpg"
                            alt="?" style="width: 50%; height:50%; opacity: 60%">
                        <div class="cover">
                            <p class="ml-2 movie-description">
                                ${descriptions[i]}
                            </p>
                        </div>
                    </div>
                </a>
            </div>`;
          $("#blind-date-movies").append(html);
        }
      }
    },
    error: function (error) {
      $("#content-container").show();
      $("#loading-overlay").hide();
      $("#movies-container").hide();

      console.log("Error:", error);
    },
  });
}

$(document).ready(function () {
  // and example movies to the examples-row
  $.each(exampleMovies, function (_, movie) {
    $("#examples-row").append(
      `<div class="mr-3">
            <a href="${movie.link}" target="_blank">
                <div class="book">
                    <img src="${movie.img}" alt="Book Image">
                    <div class="cover">
                        <p class="ml-2">${movie.description}</p>
                    </div>
                </div>
            </a>
        </div>`
    );
  });

  // Attach toggleContainers function to the click event of the togglebutton
  $("#toggleButton").click(toggleContainers);
});
