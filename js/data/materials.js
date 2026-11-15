// Floor Finish Materials Catalog & Estimating
export const MATS = {
  marble:  {name:{zh:'رخام إيطالي كالاتا مصقول', en:'Polished Italian Calacatta Marble'}, price:680, sw:'#f6f3ee'},
  wood:    {name:{zh:'باركيه خشب بلوط فرنسي فاخر', en:'French Oak Natural Parquet'}, price:380, sw:'#c9985d'},
  walnut:  {name:{zh:'باركيه خشب جوز ملكي داكن', en:'Dark American Walnut Flooring'}, price:420, sw:'#724c30'},
  tile800: {name:{zh:'بورسلان بيج دافئ كبير 800×800', en:'Warm Ivory Porcelain Tiles 800x800'}, price:240, sw:'#ebe5d9'},
  tile600: {name:{zh:'بورسلان رمادي حجري للمطبخ 600×600', en:'Modern Slate Kitchen Tiles 600x600'}, price:190, sw:'#596168'},
  antislip:{name:{zh:'حجر مانع للانزلاق للحمامات', en:'Textured Non-Slip Bathroom Stone'}, price:170, sw:'#3d444b'},
  terrace: {name:{zh:'خشب تيك طبيعي للتراس الخارجي', en:'Natural Teak Outdoor Decking'}, price:340, sw:'#ad7d52'},
  terrazzo:{name:{zh:'تيرازو فينيسي مودرن للتراس', en:'Venetian Terrazzo Balcony Tiles'}, price:290, sw:'#e4ddcf'},
  carpet:  {name:{zh:'سجاد صوف فاخر', en:'Plush Wool Carpet'}, price:220, sw:'#b8b0c4'},
};

// Interior Wall Paints, Regional Heritage Plasters & Textures Catalog
export const WALL_PAINTS = {
  // 🇸🇦 KSA & Regional Heritage Finishes
  salmani: {
    name: { zh: 'طراز سلماني - جص أبيض فاخر', en: 'Salmani Architectural Alabaster' },
    category: 'ksa',
    price: 45,
    sw: '#f6f4ee',
    roughness: 0.94,
    desc: 'جص معماري أبيض ناعم مستوحى من كود العمارة السلمانية الفاخرة'
  },
  najdi_clay: {
    name: { zh: 'طين نجد - لياسة طينية تراثية دافئة', en: 'Najdi Diriyah Clay Plaster' },
    category: 'ksa',
    price: 65,
    sw: '#cbb296',
    roughness: 0.96,
    hasTexture: true,
    desc: 'لياسة طين طبيعي دافئ بحبيبات ناعمة وقش تحاكي تراث الدرعية التاريخية'
  },
  hejaz_stone: {
    name: { zh: 'حجر المنجور الحجازي - جدة التاريخية', en: 'Hejaz Al-Balad Coral Stone' },
    category: 'ksa',
    price: 70,
    sw: '#e6ddcf',
    roughness: 0.92,
    hasTexture: true,
    desc: 'ملمس حجري ناعم مستوحى من مباني جدة التاريخية وحجر المنجور البحري'
  },
  asir_green: {
    name: { zh: 'أخضر عرعر عسيري - تراث الجنوب', en: 'Asir Highland Juniper Green' },
    category: 'ksa',
    price: 55,
    sw: '#384c3e',
    roughness: 0.85,
    desc: 'أخضر نباتي عميق مستوحى من مرتفعات عسير وأشجار العرعر الطبيعية'
  },
  navy: {
    name: { zh: 'كحلي لؤلؤي خليجي - أزرق الخليج', en: 'Arabian Gulf Deep Indigo' },
    category: 'ksa',
    price: 58,
    sw: '#1c2a38',
    roughness: 0.80,
    desc: 'كحلي داكن ملكي عميق مستلهم من تراث الغوص ومياه الخليج العربي'
  },
  desert: {
    name: { zh: 'بيج رمل الصحراء - نفود الرياض', en: 'Riyadh Dune Warm Sand' },
    category: 'ksa',
    price: 40,
    sw: '#e2d5c1',
    roughness: 0.88,
    desc: 'لون رملي ذهبي دافئ يمنح المساحات رحابة وأصالة صحراوية هادئة'
  },

  // ✨ Minimalist Wall Textures & Architectural Slats
  wood_slats: {
    name: { zh: 'بديل خشب - شرائح بلوط مودرن', en: 'Modern Natural Oak Slats' },
    category: 'texture',
    price: 160,
    sw: '#c59b6c',
    roughness: 0.40,
    hasTexture: true,
    desc: 'شرائح خشبية عمودية مخددة بفواصل ظل غائرة لتجويفات التلفزيون والمجالس'
  },
  walnut_slats: {
    name: { zh: 'بديل خشب - شرائح جوز داكن فاخر', en: 'Smoked Walnut Fluted Slats' },
    category: 'texture',
    price: 185,
    sw: '#5c3e29',
    roughness: 0.38,
    hasTexture: true,
    desc: 'شرائح خشب جوز أمريكي داكن فاخر للجدران الرئيسية وغرف النوم الماستر'
  },
  marble_slab: {
    name: { zh: 'رخام كالاتا جداري - عروق ذهبية', en: 'Calacatta Gold Porcelain Slab' },
    category: 'texture',
    price: 280,
    sw: '#fcfaf6',
    roughness: 0.12,
    metalness: 0.05,
    hasTexture: true,
    desc: 'ألواح بورسلان رخامية كبيرة الحجم بلمعان مصقول وعروق ذهبية رمادية متناسقة'
  },
  woven_linen: {
    name: { zh: 'ورق جدران كتان طبيعي بيج هادئ', en: 'Woven Natural Linen Wallcovering' },
    category: 'texture',
    price: 75,
    sw: '#ded5c3',
    roughness: 0.95,
    hasTexture: true,
    desc: 'نسيج كتاني طبيعي محبوك بملمس صوتي هادئ للممرات وغرف النوم'
  },
  microcement: {
    name: { zh: 'مايكروسمنت رمادي ناعم مودرن', en: 'Troweled Architectural Microcement' },
    category: 'texture',
    price: 120,
    sw: '#cbcece',
    roughness: 0.72,
    hasTexture: true,
    desc: 'خرسانة ناعمة بحركات مالج يدوية انسيابية للمظهر المودرن المينيماليست'
  },

  // 🎨 Minimalist Contemporary Paints
  alabaster: {
    name: { zh: 'بياض عاجي دافئ فاخر', en: 'Warm Luxury Alabaster' },
    category: 'paint',
    price: 35,
    sw: '#f7f4eb',
    roughness: 0.92,
    desc: 'الدهان المعماري الأساسي فائق النعومة والمناسب لجميع المساحات'
  },
  greige: {
    name: { zh: 'غريج بيج كلاسيكي ناعم', en: 'Contemporary Warm Greige' },
    category: 'paint',
    price: 38,
    sw: '#dad3c5',
    roughness: 0.90,
    desc: 'مزيج الغريج العصري الأنيق المعتمد في أرقى التصاميم المعمارية'
  },
  mist: {
    name: { zh: 'رمادي ضبابي هادئ عصري', en: 'Soft Studio Mist Gray' },
    category: 'paint',
    price: 38,
    sw: '#d4d8db',
    roughness: 0.88,
    desc: 'رمادي فاتح هادئ يعكس الإضاءة الطبيعية بسلاسة'
  },
  sage: {
    name: { zh: 'أخضر ميرمية إسكندنافي هادئ', en: 'Nordic Sage Green' },
    category: 'paint',
    price: 45,
    sw: '#9ca89b',
    roughness: 0.85,
    desc: 'أخضر باهت مهدئ للأعصاب يتماشى مع الأثاث الخشبي والنباتات'
  },
  terracotta: {
    name: { zh: 'تيراكوتا ترابي أندلسي دافئ', en: 'Earthy Andalusian Terracotta' },
    category: 'paint',
    price: 48,
    sw: '#b4654d',
    roughness: 0.84,
    desc: 'طين محروق دافئ يضفي روح البحر الأبيض المتوسط والدفء العائلي'
  },
  charcoal: {
    name: { zh: 'رمادي فحمي مودرن مطفأ', en: 'Matte Studio Charcoal' },
    category: 'paint',
    price: 50,
    sw: '#383e44',
    roughness: 0.80,
    desc: 'فحمي مخملي عميق لجدران التميز في الصالونات ووحدات التلفزيون'
  }
};

