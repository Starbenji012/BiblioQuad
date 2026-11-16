const express = require('express');
const path = require('path');
const routes = require('./routes');
const app = express();
app.set('view engine','ejs'); app.set('views',path.join(__dirname,'views'));
app.use(express.urlencoded({ extended:false })); app.use(express.static(path.join(__dirname,'public'))); app.use(routes);
app.use((err,req,res,next) => { res.status(500).send('Erreur serveur : ' + err.message); });
app.listen(process.env.PORT || 3000, () => console.log('Node library on port ' + (process.env.PORT || 3000)));
