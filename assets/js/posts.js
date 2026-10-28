const loadMoreBtn = document.querySelector('#loadMore');
const boxes = [...document.querySelectorAll('.cards__grid .card__item')];
let currentItem = 6;
boxes.slice(currentItem).forEach(box => { box.hidden = true; });
loadMoreBtn.hidden = currentItem >= boxes.length;
loadMoreBtn.onclick = () => {
  boxes.slice(currentItem, currentItem + 3).forEach(box => {
    box.hidden = false;
  });
  currentItem += 3;
  loadMoreBtn.hidden = currentItem >= boxes.length;
};
