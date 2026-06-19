smartdesign.connect().then(sdapi => {
  document.getElementById('my-button').addEventListener('click', () => {
    const cui = 14942091;

    fetch("http://localhost:3001", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify([{ cui: cui, data: new Date().toISOString().split("T")[0] }])
    })
    .then(r => r.json())
    .then(data => {
      const denumire = data.found[0].date_generale.denumire;
      console.log("Nume firmă:", denumire);

      sdapi.fetch("v7.0/type/address/full")
        .then(r => r.json())
        .then(records => {
          const record = records.find(r => r.fields.TAXNUMBER === String(cui));
          if (!record) { console.log("Nu s-a găsit înregistrarea cu CUI-ul dat"); return; }

          sdapi.fetch(`v7.0/type/address/${record.id}`)
            .then(r => {
              const etag = r.headers.get('ETag');
              return r.json().then(fullRecord => ({ fullRecord, etag }));
            })
            .then(({ fullRecord, etag }) => {
              const updatedFields = { ...fullRecord.fields, COMPNAME: denumire };
              sdapi.fetch(`v7.0/type/address/${record.id}`, {
                method: "PUT",
                headers: { "If-Match": etag },
                body: JSON.stringify({
                  objectType: fullRecord.objectType,
                  id: fullRecord.id,
                  fields: updatedFields
                })
              }).then(r => {
                console.log("Status:", r.status);
                return r.text();
              }).then(result => console.log("Raspuns PUT:", result));
            });
        });
    })
    .catch(err => console.error("Eroare ANAF:", err));
  });
});