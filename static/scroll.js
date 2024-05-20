gsap.registerPlugin(ScrollTrigger);

const sections = gsap.utils.toArray(".section");
// scroll snapping only for big screens
ScrollTrigger.matchMedia({
    "(min-width: 1000px)": function() {
      // ScrollTriggers for larger screens
      sections.forEach((section, i) => {
        ScrollTrigger.create({
          trigger: section,
          start: "top",
          end: "bottom",
          //snapscroll
          pin: true,
        });
      });
    },
  });