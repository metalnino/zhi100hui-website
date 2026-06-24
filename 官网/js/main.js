// 移动端导航：点击链接后自动收起菜单
document.addEventListener('click', function (e) {
  var links = document.getElementById('navlinks');
  if (!links) return;
  if (e.target.matches('.nav-links a')) {
    links.classList.remove('open');
  }
});
