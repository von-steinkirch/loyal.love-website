async function includeHTML(elementId, contentPath, basePath = './') {
  const element = document.getElementById(elementId);
  if (element) {
    try {
      const response = await fetch(`${basePath}shared/${contentPath}`);
      const html = await response.text();
      element.innerHTML = html;
    } catch (error) {
      console.error(`Error loading shared ${contentPath}:`, error);
    }
  }
}

function includeTitle(elementId, basePath = './') {
  return includeHTML(elementId, 'title.html', basePath);
}

function includeFooter(elementId, basePath = './') {
  return includeHTML(elementId, 'footer.html', basePath);
}
