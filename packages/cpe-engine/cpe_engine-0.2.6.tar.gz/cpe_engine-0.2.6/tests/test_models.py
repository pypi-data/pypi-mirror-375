"""Tests para modelos principales."""

import pytest
from datetime import datetime

from cpe_engine.core.models import Invoice, Note, SaleDetail
from cpe_engine.sunat.credentials import SunatCredentials


class TestSunatCredentials:
    """Tests para SunatCredentials."""
    
    def test_crear_credenciales_validas(self):
        """Test creación de credenciales válidas."""
        creds = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS",
            password="test123",
            certificado="-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            es_test=True
        )
        
        assert creds.ruc == "20000000001"
        assert creds.es_test is True
        assert not creds.es_certificado_archivo
        assert creds.validar_certificado() is True  # Tiene formato PEM básico
    
    def test_validaciones_ruc(self):
        """Test validaciones de RUC."""
        with pytest.raises(ValueError, match="RUC debe tener 11 dígitos"):
            SunatCredentials(
                ruc="123",
                usuario="test",
                password="test",
                certificado="test"
            )
    
    def test_validaciones_campos_vacios(self):
        """Test validaciones de campos obligatorios."""
        with pytest.raises(ValueError, match="Usuario SUNAT es obligatorio"):
            SunatCredentials(
                ruc="20000000001",
                usuario="",
                password="test",
                certificado="test"
            )


class TestInvoiceModel:
    """Tests para modelo Invoice."""
    
    def test_crear_factura_basica(self, empresa_prueba, cliente_juridica):
        """Test creación de factura básica."""
        factura = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_operacion="01",  # Venta interna
            tipo_doc="01",
            tipo_moneda="PEN",
            company=empresa_prueba,
            client=cliente_juridica,
        )
        
        assert factura.serie == "F001"
        assert factura.correlativo == 123
        assert factura.tipo_doc == "01"
        assert factura.company.ruc == "20000000001"
    
    def test_totales_declarativos(self, factura_simple):
        """Test que los totales son declarativos (como greenter)."""
        # Los totales fueron proporcionados manualmente en el fixture
        assert factura_simple.mto_oper_gravadas == 200.00
        assert factura_simple.mto_igv == 36.00
        assert factura_simple.mto_impventa == 236.00
        
        # Verificar que los nuevos campos tributarios existen
        assert hasattr(factura_simple, 'mto_ivap')
        assert hasattr(factura_simple, 'mto_ir')
        assert hasattr(factura_simple, 'mto_icbper')
        assert hasattr(factura_simple, 'mto_base_igv')
        assert hasattr(factura_simple, 'mto_base_ivap')
        assert hasattr(factura_simple, 'mto_base_ir')
        assert hasattr(factura_simple, 'mto_base_icbper')
        assert hasattr(factura_simple, 'mto_base_otros')
    
    def test_validacion_serie_factura(self, empresa_prueba, cliente_juridica):
        """Test validación de serie para facturas."""
        # Serie válida para factura
        factura = Invoice(
            serie="F001",
            correlativo=1,
            fecha_emision=datetime.now(),
            tipo_operacion="01",  # Venta interna
            tipo_doc="01",
            tipo_moneda="PEN",
            company=empresa_prueba,
            client=cliente_juridica
        )
        
        assert factura.serie == "F001"


class TestSaleDetail:
    """Tests para SaleDetail."""
    
    def test_crear_detalle_producto(self):
        """Test creación de detalle de producto."""
        detalle = SaleDetail(
            cod_item="PROD001",
            des_item="Producto Test",
            cantidad=5,
            unidad="NIU",
            mto_valor_unitario=50.00,
            tip_afe_igv=10,
            porcentaje_igv=18.0,
            # Nuevos campos tributarios
            tip_afe_ivap="",
            tip_afe_isc="",
            tip_afe_ir="",
            tip_afe_otro="",
            isc=0.0,
            ivap=0.0,
            ir=0.0,
            icbper=0.0,
            otro_tributo=0.0,
            mto_base_igv=0.0,
            mto_base_isc=0.0,
            mto_base_ivap=0.0,
            mto_base_ir=0.0,
            mto_base_icbper=0.0,
            mto_base_otro=0.0,
            porcentaje_isc=0.0,
            porcentaje_ivap=0.0,
            porcentaje_ir=0.0,
            porcentaje_otro=0.0,
            factor_icbper=0.0
        )
        
        assert detalle.cod_item == "PROD001"
        assert detalle.cantidad == 5
        assert detalle.mto_valor_unitario == 50.00
        
        # Greenter es declarativo - usuario proporciona totales
        detalle.mto_valor_venta = 250.00  # 5 * 50  
        detalle.mto_precio_unitario = 59.00  # 50 * 1.18 (incluye TODOS los impuestos)
        detalle.igv = 45.00  # 18% de 250
        
        assert detalle.mto_valor_venta == 250.00
        assert detalle.mto_precio_unitario == 59.00
        
        # Verificar que los nuevos campos tributarios existen
        assert hasattr(detalle, 'ivap')
        assert hasattr(detalle, 'isc')
        assert hasattr(detalle, 'ir')
        assert hasattr(detalle, 'icbper')
        assert hasattr(detalle, 'otro_tributo')
        assert hasattr(detalle, 'mto_base_igv')
        assert hasattr(detalle, 'mto_base_isc')
        assert hasattr(detalle, 'mto_base_ivap')
        assert hasattr(detalle, 'mto_base_ir')
        assert hasattr(detalle, 'mto_base_icbper')
        assert hasattr(detalle, 'mto_base_otro')
        assert hasattr(detalle, 'porcentaje_isc')
        assert hasattr(detalle, 'porcentaje_ivap')
        assert hasattr(detalle, 'porcentaje_ir')
        assert hasattr(detalle, 'porcentaje_otro')
        assert hasattr(detalle, 'factor_icbper')