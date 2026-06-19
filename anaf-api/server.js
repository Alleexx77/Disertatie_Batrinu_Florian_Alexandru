const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

app.post("/anaf", async (req, res) => {
    try {
        const cui = req.body.cui;

        if (!cui) {
            return res.status(400).send("CUI lipsa");
        }

        const payload = [
            {
                cui: parseInt(cui.replace("RO", "")),
                data: new Date().toISOString().split("T")[0]
            }
        ];

        const response = await axios.post(
            "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva",
            payload
        );

        if (!response.data.found || response.data.found.length === 0) {
            return res.send({ denumire: "Nu a fost gasita" });
        }

        const firma = response.data.found[0].date_generale;

        res.send({
            denumire: firma.denumire
        });

    } catch (err) {
        console.log(err.message);
        res.status(500).send("Eroare");
    }
});

app.listen(3000, "0.0.0.0", () => console.log("Server pornit pe port 3000"));