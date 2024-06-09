//example moviesconst
exampleMovies = [
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

$(document).ready(function() {
    // Iterate through exampleMovies and add them to the examples-row
    $.each(exampleMovies, function(index, movie) {
        $('#examples-row').append(
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
});
