import scrapy

class Propiedades(scrapy.Spider):
    name = "propiedades"

    custom_settings = {
        # Omitir bloqueo de bots
        'ROBOTSTXT_OBEY': False,
        
        # User agent simula mac
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        
        # Cabeceras extra que mandan los navegadores reales
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        },
        # Guardar archivo en utf-8
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
    }

    def start_requests(self):
        #url = ["https://inmuebles.mercadolibre.com.mx/departamentos/distrito-federal/#applied_filter_id%3DPROPERTY_TYPE%26applied_filter_name%3DInmueble%26applied_filter_order%3D1%26applied_value_id%3D242062%26applied_value_name%3DDepartamentos%26applied_value_order%3D2%26applied_value_results%3D38298%26is_custom%3Dfalse"]
        url = ["https://inmuebles.mercadolibre.com.mx/departamentos/distrito-federal/"]
        yield scrapy.Request(url=url[0], callback=self.parse)

    def parse(self, response):
        # Buscar contenedor padre principal
        contenedores = response.xpath('//li[contains(@class, "ui-search-layout__item")]')
        
        # Si no encuentra los <li>, entonces buscar los <div>
        if not contenedores:
            contenedores = response.xpath('//div[contains(@class, "poly-card")]')
        
        for casa in contenedores:
            precio = casa.xpath('.//span[contains(@class, "andes-money-amount")]/@aria-label').get()
            direccion = casa.xpath('.//span[contains(@class, "poly-component__location")]/text()').get()
            
            # Filtro: Si no hay precio ni dirección, saltar al siguiente
            if not precio and not direccion:
                continue
                
            recamaras = casa.xpath('.//li[contains(@class, "poly-attributes_list__item") and (contains(text(), "dormitorios") or contains(text(), "dormitorio") or contains(text(), "recámaras") or contains(text(), "recámara"))]/text()').get()
            banos = casa.xpath('.//li[contains(@class, "poly-attributes_list__item") and (contains(text(), "baño") or contains(text(), "baños"))]/text()').get()
            m2 = casa.xpath('.//li[contains(@class, "poly-attributes_list__item") and contains(text(), "m²")]/text()').get()

            yield {
                'precio': precio,
                'direccion': direccion,
                'recamaras': recamaras,
                'banos': banos,
                'm2': m2,
            }

        siguiente_pagina = response.xpath(
            '//li[contains(@class, "andes-pagination__button--next")]//a/@href | '
            '//a[.//span[contains(text(), "Siguiente")]]/@href | '
            '//a[@title="Siguiente"]/@href'
        ).get()
        
        self.logger.info(f"URL del botón Siguiente encontrada: {siguiente_pagina}")

        if siguiente_pagina:
            yield response.follow(url=siguiente_pagina, callback=self.parse)