smartdesign.connect().then(api => {
  const cui = api.State.current.ref.formattedValue;
  console.log("CUI:", cui);

  document.getElementById('my-button').addEventListener('click', () => {
    fetch("http://localhost:3001", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify([{ cui: parseInt(cui), data: new Date().toISOString().split("T")[0] }])
    })
    .then(r => r.json())
    .then(data => {
      if (!data.found || data.found.length === 0) {
        console.log("CUI-ul nu a fost găsit în ANAF");
        return;
      }

      const d = data.found[0];

      api.State.current.ref2.value = d.date_generale.denumire;
      api.State.current.ref3.value = d.adresa_sediu_social.sdenumire_Strada + " " + d.adresa_sediu_social.snumar_Strada;
      api.State.current.ref4.value = d.date_generale.telefon;
      api.State.current.ref5.value = d.adresa_sediu_social.scod_Postal;
      api.State.current.ref6.value = d.date_generale.nrRegCom;
      api.State.current.ref7.value = d.date_generale.iban;
      api.State.current.ref8.value = d.adresa_sediu_social.sdenumire_Localitate;
      api.State.current.ref9.value = d.adresa_sediu_social.sdenumire_Judet;
      api.State.current.ref10.value = d.inregistrare_scop_Tva.scpTVA ? "DA" : "NU";

      api.State.update();
      console.log("Campuri actualizate cu succes!");
    })
    .catch(err => console.error("Eroare ANAF:", err));
  });
});