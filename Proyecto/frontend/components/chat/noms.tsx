import Image from "next/image";

type Language = "es" | "en";
type NomsData = {
  [lang in Language]: {
    [nom: string]: string;
  };
};

const Noms: NomsData = {
  en: {
    "NOM-051-SCFI-2010": "/noms/english/Etiqueta11.png",
    "NOM-020-SCFI-1997": "/noms/english/Etiqueta14.png",
    "NOM-141-SCFI-2012": "/noms/english/Etiqueta12.png",
    "NOM-004-SCFI-2006": "/noms/english/Etiqueta13.png",
    "NOM-050-SCFI-2004": "/noms/english/Etiqueta10.png",
    "NOM-116-SCFI-1997": "/noms/english/Etiqueta16.png",
    "NOM-186-SCFI-2013": "/noms/english/Etiqueta17.png",
    "NOM-003-SCFI-2014": "/noms/english/Etiqueta15.png",
  },
  es: {
    "NOM-051-SCFI-2010": "/noms/spanish/Etiqueta02.png",
    "NOM-020-SCFI-1997": "/noms/spanish/Etiqueta05.png",
    "NOM-141-SCFI-2012": "/noms/spanish/Etiqueta03.png",
    "NOM-004-SCFI-2006": "/noms/spanish/Etiqueta04.png",
    "NOM-050-SCFI-2004": "/noms/spanish/Etiqueta01.png",
    "NOM-116-SCFI-1997": "/noms/spanish/Etiqueta07.png",
    "NOM-186-SCFI-2013": "/noms/spanish/Etiqueta08.png",
    "NOM-003-SCFI-2014": "/noms/spanish/Etiqueta06.png",
  },
};

export const NomsMessage = ({ nom, lang }: { nom: string; lang: Language }) => {
  const urlPublicImage = Noms[lang]?.[nom];

  if (!urlPublicImage) {
    return;
  }

  return (
    <div className="my-2 relative w-full h-[580px] border border-neutral-200 rounded-2xl overflow-hidden">
      <Image
        src={urlPublicImage}
        alt={`Representation of Nom ${nom} in language ${lang}`}
        layout="fill"
        objectFit="contain"
        priority
      />
    </div>
  );
};
