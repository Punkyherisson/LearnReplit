<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Faire un Fichier CSV des applications Replit dans la console
Pour créer un fichier CSV contenant la liste propre de tes projets Replit (nom, visibilité, URL), voici un script JavaScript à coller dans la console de la page « Mes Repls » de Replit. Ce script extrait les données, supprime les doublons, et génère un fichier CSV téléchargeable automatiquement :

```javascript
async function scrollToEnd() {
  let lastHeight = 0;
  while (document.documentElement.scrollHeight !== lastHeight) {
    lastHeight = document.documentElement.scrollHeight;
    window.scrollTo(0, document.documentElement.scrollHeight);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

function downloadCSV(csv, filename) {
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

async function getReplsListCSV() {
  await scrollToEnd();
  const repls = Array.from(document.querySelectorAll('a[href^="/@"]'));

  // Collect unique projects by URL
  const unique = new Map();
  repls.forEach(a => {
    const url = a.href;
    const name = a.textContent.trim();
    // Detect visibility by presence of "Private" or "svg" in innerHTML for cadenas icon
    const visibility = a.innerHTML.includes('svg') ? 'Privé' : 'Public';
    if (!unique.has(url)) {
      unique.set(url, { name, url, visibility });
    }
  });

  // Construct CSV content
  let csv = 'Visibilité,Nom,URL\n';
  unique.forEach(({visibility, name, url}) => {
    // Escape quotes and commas in name if any
    const cleanName = `"${name.replace(/"/g, '""')}"`;
    csv += `${visibility},${cleanName},${url}\n`;
  });

  downloadCSV(csv, 'Replit_Projects_List.csv');
  alert('Le fichier CSV a été généré et téléchargé !');
}

getReplsListCSV();
```


### Mode d’emploi

1. Va sur https://replit.com/~ (page « Mes Repls »).
2. Ouvre la console de ton navigateur (F12 → onglet Console).
3. Colle tout le script ci-dessus.
4. Appuie sur Entrée pour l’exécuter.
5. Un fichier nommé **Replit_Projects_List.csv** sera automatiquement téléchargé avec la liste propre de tes projets.

Tu pourras ouvrir ce fichier CSV ensuite dans Excel, LibreOffice Calc ou un autre tableur pour une gestion simple et claire de tes projets Replit.
Si tu souhaites un format particulier ou autre type d’export, n’hésite pas à demander.

