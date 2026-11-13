// Indique à la page qu'elle tourne dans l'appli Windows (textes légaux de l'appli, pas du site).
const { contextBridge } = require('electron');
contextBridge.exposeInMainWorld('EASYCODE_DESKTOP', true);
