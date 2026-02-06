// Mock data для демонстрации когда API недоступен
export const mockFactions = [
  {
    id: "6cdc473b-868d-476d-b3ba-9e8f5529b15e",
    code: "gov",
    name: "Правительство",
    description: "Центральный орган управления",
    created_at: new Date().toISOString()
  },
  {
    id: "7d5e384c-979e-587e-c4cb-0f9g6630c26f",
    code: "fsb",
    name: "ФСБ",
    description: "Федеральная служба безопасности",
    created_at: new Date().toISOString()
  },
  {
    id: "8e6f495d-080f-698f-d5dc-1g0h7741d37g",
    code: "gibdd",
    name: "ГИБДД",
    description: "Государственная инспекция безопасности дорожного движения",
    created_at: new Date().toISOString()
  },
  {
    id: "9f7g5a6e-191g-7a9g-e6ed-2h1i8852e48h",
    code: "umvd",
    name: "УМВД",
    description: "Управление Министерства внутренних дел",
    created_at: new Date().toISOString()
  },
  {
    id: "a08h6b7f-2a2h-8b0h-f7fe-3i2j9963f59i",
    code: "army",
    name: "Армия",
    description: "Вооружённые силы",
    created_at: new Date().toISOString()
  },
  {
    id: "b19i7c8g-3b3i-9c1i-g8gf-4j3k0a74g60j",
    code: "hospital",
    name: "Больница",
    description: "Медицинское учреждение",
    created_at: new Date().toISOString()
  },
  {
    id: "c20j8d9h-4c4j-0d2j-h9hg-5k4l1b85h71k",
    code: "smi",
    name: "СМИ",
    description: "Средства массовой информации",
    created_at: new Date().toISOString()
  },
  {
    id: "d31k9e0i-5d5k-1e3k-i0ih-6l5m2c96i82l",
    code: "fsin",
    name: "ФСИН",
    description: "Федеральная служба исполнения наказаний",
    created_at: new Date().toISOString()
  }
];

export const mockDepartments = {
  fsb: [
    {
      id: "dept-fsb-1",
      faction_id: "7d5e384c-979e-587e-c4cb-0f9g6630c26f",
      name: "Отдел контрразведки",
      head_user_id: null,
      deputy_user_ids: [],
      created_at: new Date().toISOString()
    }
  ]
};
