import "./styles/theme.scss";
import "./styles/theme.scss";
// import "bootstrap";

const heightWidthRatio = 0.33;

const createWatermark = (el, width, height, repeat) => {
  const watermark = document.createElement("div");
  watermark.classList.add("watermark");
  const wSize = height + width;
  watermark.style.height = wSize + "px";
  watermark.style.width = wSize + "px";
  watermark.style.left = -wSize / 2 + width / 2 + "px";
  watermark.style.top = -wSize / 2 + height / 2 + "px";
  watermark.dataset.text = (el.dataset.watermark + " – ").repeat(repeat);
  el.appendChild(watermark);
};

const autoWatermark = (el) => {
  const lengthMultiplier = Math.round(el.dataset.watermark.length);
  const repeat = Math.round(
    el.offsetHeight * heightWidthRatio * lengthMultiplier
  );
  if (el.dataset.watermark) {
    createWatermark(el, el.offsetWidth, el.offsetHeight, repeat);
  }
};

const cleanWatermarks = () => {
  document.querySelectorAll(".watermark").forEach(function (el) {
    el.parentNode.removeChild(el);
  });
};

const applyWatermarks = () => {
  document.querySelectorAll(".watermarked").forEach(function (el) {
    autoWatermark(el);
  });
};

document.addEventListener("DOMContentLoaded", function (event) {
  // const popoverTriggerList = document.querySelectorAll(
  //   '[data-bs-toggle="popover"]'
  // );
  // console.log(popoverTriggerList);
  // [...popoverTriggerList].map(
  //   (popoverTriggerEl) => new Popover(popoverTriggerEl)
  // );
  applyWatermarks();
  if (typeof Faceted != "undefined") {
    jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function () {
      setTimeout(() => {
        cleanWatermarks();
        applyWatermarks();
      }, 100);
    });
  }
});

document.addEventListener("ItemsLayoutChanged", function (event) {
  cleanWatermarks();
  applyWatermarks();
});

// if (module.hot) {
//   module.hot.accept();
// }
