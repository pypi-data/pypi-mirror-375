"""Modelo BaseSale - clase base para todos los comprobantes de venta."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union

from .client import Client
from .company import Company
from .payment_terms import PaymentTerms, Cuota
# Imports de catálogos removidos - validaciones están en capa separada (validator/)


@dataclass
class Legend:
    """Leyenda del comprobante."""
    code: str
    value: str


class SaleDetail:
    """
    Detalle de línea de venta con convención snake_case estándar.
    
    IMPORTANTE: Como el paquete es DECLARATIVO, el usuario debe proporcionar
    TODOS los valores calculados. No se calculan automáticamente.
    
    Nomenclatura: Usa snake_case consistente (cod_item, des_item, mto_valor_unitario)
    equivalente al camelCase de Greenter (codItem, desItem, mtoValorUnitario).
    """
    
    def __init__(self,
                 # ==========================================
                 # CAMPOS OBLIGATORIOS (REQUERIDOS)
                 # ==========================================
                 cod_item: str,                                       # OBLIGATORIO: Código del producto (snake_case estándar)
                 des_item: str,                                       # OBLIGATORIO: Descripción del producto (snake_case estándar)
                 cantidad: float,                                     # OBLIGATORIO: Cantidad (debe ser > 0)
                 mto_valor_unitario: float,                           # REQUERIDO: Valor unitario SIN impuestos
                 mto_precio_unitario: float = 0.0,                    # REQUERIDO: Precio unitario CON TODOS los impuestos
                 mto_valor_venta: float = 0.0,                        # REQUERIDO: Total de la línea SIN IGV
                 igv: float = 0.0,                                    # REQUERIDO: IGV de la línea
                 tip_afe_igv: int = 10,                              # REQUERIDO: Código de afectación IGV ("10"=Gravado, "40"=Exportación, etc.)
                 
                 # ==========================================
                 # CAMPOS OPCIONALES CON DEFAULT
                 # ==========================================
                 unidad: str = "NIU",                                 # OPCIONAL: Unidad de medida ("NIU", "KGM", "ZZ", etc.)
                 total_impuestos: float = 0.0,                       # OPCIONAL: Total de impuestos (suma de todos los tributos)
                 porcentaje_igv: float = 18.0,                       # OPCIONAL: Porcentaje de IGV (18% por defecto)
                 mto_precio_unitario_final: float = 0.0,             # OPCIONAL: Precio unitario final
                 
                 # ==========================================
                 # NUEVOS CAMPOS TRIBUTARIOS (OPCIONALES)
                 # ==========================================
                 # Campos de afectación por tributo
                 tip_sis_isc: str = "",                              # OPCIONAL: Sistema de cálculo ISC (Catálogo 08)
                 tip_afe_ir: str = "",                               # OPCIONAL: Código afectación IR
                 tip_afe_otro: str = "",                             # OPCIONAL: Código afectación otros tributos
                 
                 # Montos de impuestos específicos
                 isc: float = 0.0,                                   # OPCIONAL: Monto ISC del item
                 ir: float = 0.0,                                    # OPCIONAL: Monto IR del item
                 icbper: float = 0.0,                                # OPCIONAL: Monto ICBPER del item
                 otro_tributo: float = 0.0,                          # OPCIONAL: Monto otro tributo específico
                 
                 # Bases imponibles específicas
                 mto_base_igv: float = 0.0,                          # OPCIONAL: Base específica para IGV
                 mto_base_isc: float = 0.0,                          # OPCIONAL: Base específica para ISC
                 mto_base_ir: float = 0.0,                           # OPCIONAL: Base específica para IR
                 mto_base_icbper: float = 0.0,                       # OPCIONAL: Base específica para ICBPER
                 mto_base_otro: float = 0.0,                         # OPCIONAL: Base específica para otro tributo
                 
                 # Porcentajes y factores
                 porcentaje_isc: float = 0.0,                        # OPCIONAL: Porcentaje ISC
                 porcentaje_ir: float = 0.0,                         # OPCIONAL: Porcentaje IR
                 porcentaje_otro: float = 0.0,                       # OPCIONAL: Porcentaje otro tributo
                 factor_icbper: float = 0.0,                         # OPCIONAL: Factor ICBPER (ej: 0.10)
                 
                 # ==========================================
                 # CAMPOS AVANZADOS (OPCIONALES)
                 # ==========================================
                 mto_valor_gratuito: float = 0.0,                    # OPCIONAL: Valor referencial para operaciones gratuitas
                 cargos: list = None,                                 # OPCIONAL: Lista de Charge (cargos a nivel detalle)
                 descuentos: list = None):                            # OPCIONAL: Lista de Charge (descuentos a nivel detalle)
        
        # Usar solo convención snake_case estándar (más sólida)
        self.cod_item = cod_item
        self.des_item = des_item
        self.unidad = unidad
        self.cantidad = cantidad
        self.mto_valor_unitario = mto_valor_unitario
        self.mto_precio_unitario = mto_precio_unitario
        self.mto_valor_venta = mto_valor_venta
        self.igv = igv
        self.total_impuestos = total_impuestos
        self.tip_afe_igv = str(tip_afe_igv)  # Convertir a string
        self.porcentaje_igv = porcentaje_igv
        self.mto_precio_unitario_final = mto_precio_unitario_final
        
        # Nuevos campos tributarios
        self.tip_sis_isc = tip_sis_isc
        self.tip_afe_ir = tip_afe_ir
        self.tip_afe_otro = tip_afe_otro
        
        self.isc = isc
        self.ir = ir
        self.icbper = icbper
        self.otro_tributo = otro_tributo
        
        self.mto_base_igv = mto_base_igv
        self.mto_base_isc = mto_base_isc
        self.mto_base_ir = mto_base_ir
        self.mto_base_icbper = mto_base_icbper
        self.mto_base_otro = mto_base_otro
        
        self.porcentaje_isc = porcentaje_isc
        self.porcentaje_ir = porcentaje_ir
        self.porcentaje_otro = porcentaje_otro
        self.factor_icbper = factor_icbper
        
        # Nuevos campos para compatibilidad con greenter
        self.mto_valor_gratuito = mto_valor_gratuito
        self.cargos = cargos or []
        self.descuentos = descuentos or []
        
        # Solo validaciones básicas de negocio
        self._validar_campos_requeridos()
    
    def _validar_campos_requeridos(self):
        """Validar solo campos básicos requeridos (sin cálculos automáticos)."""
        # Validaciones básicas de negocio
        if not self.des_item or not self.des_item.strip():
            raise ValueError("Descripción del producto es requerida")
            
        if self.cantidad < 0:
            raise ValueError(f"Cantidad no puede ser negativa, recibido: {self.cantidad}")
    
    # Validaciones SUNAT están en validator/ - core es declarativo como greenter
    # def _validar_codigos_sunat(self): -> MoveToDifferentLayer


@dataclass
class BaseSale(ABC):
    """
    Clase base para todos los comprobantes de venta.
    
    IMPORTANTE: Este paquete es DECLARATIVO como Greenter.
    - NO calcula totales automáticamente
    - El usuario debe proporcionar TODOS los campos requeridos
    - Los campos obligatorios generarán error si no se proporcionan
    """
    
    # ==========================================
    # CAMPOS OBLIGATORIOS (REQUERIDOS POR SUNAT)
    # ==========================================
    serie: str                    # OBLIGATORIO: Serie del documento (ej: "F001", "B001")
    correlativo: Union[int, str]  # OBLIGATORIO: Número correlativo (entero o string con ceros)
    fecha_emision: datetime      # OBLIGATORIO: Fecha de emisión
    tipo_doc: str               # OBLIGATORIO: "01"=Factura, "03"=Boleta, "07"=Nota Crédito, "08"=Nota Débito
    company: Optional[Company] = None    # OBLIGATORIO: Datos de la empresa emisora
    client: Optional[Client] = None      # OBLIGATORIO: Datos del cliente
    
    # ==========================================
    # CAMPOS OPCIONALES CON DEFAULT
    # ==========================================
    tipo_moneda: str = "PEN"     # OPCIONAL: Moneda ("PEN", "USD", "EUR", etc.)
    details: List[SaleDetail] = field(default_factory=list)    # OPCIONAL: Lista de items/detalles
    legends: List[Legend] = field(default_factory=list)       # OPCIONAL: Leyendas del documento
    
    # ==========================================
    # TOTALES - DECLARATIVOS (USUARIO DEBE CALCULAR)
    # ==========================================
    # IMPORTANTE: Estos campos son requeridos para generar XML válido
    # pero el paquete NO los calcula automáticamente
    
    # Montos por tipo de operación
    mto_oper_gravadas: float = 0.0      # REQUERIDO: Operaciones gravadas (sin IGV) 
    mto_oper_inafectas: float = 0.0     # OPCIONAL: Operaciones inafectas
    mto_oper_exoneradas: float = 0.0    # OPCIONAL: Operaciones exoneradas
    mto_oper_exportacion: float = 0.0   # OPCIONAL: Operaciones de exportación
    mto_oper_gratuitas: float = 0.0     # OPCIONAL: Operaciones gratuitas
    mto_igv_gratuitas: float = 0.0      # OPCIONAL: IGV de operaciones gratuitas
    
    # Tributos
    mto_igv: float = 0.0                # REQUERIDO: Total IGV 
    mto_isc: float = 0.0                # OPCIONAL: Total ISC
    mto_ir: float = 0.0                 # OPCIONAL: Total IR
    mto_icbper: float = 0.0             # OPCIONAL: Total ICBPER
    mto_ivap: float = 0.0               # OPCIONAL: Total IVAP
    mto_otros_tributos: float = 0.0     # OPCIONAL: Otros tributos
    mto_total_tributos: float = 0.0     # REQUERIDO: Total impuestos
    
    # Bases imponibles específicas
    mto_base_igv: float = 0.0           # OPCIONAL: Base específica para IGV
    mto_base_isc: float = 0.0           # OPCIONAL: Base específica para ISC
    mto_base_ir: float = 0.0            # OPCIONAL: Base específica para IR
    mto_base_icbper: float = 0.0        # OPCIONAL: Base específica para ICBPER
    mto_base_ivap: float = 0.0          # OPCIONAL: Base específica para IVAP
    mto_base_otros: float = 0.0         # OPCIONAL: Base específica para otros tributos
    
    # Total del documento
    valor_venta: float = 0.0            # REQUERIDO: Valor total de venta (suma de mto_valor_venta de items)
    mto_impventa: float = 0.0           # REQUERIDO: Importe total de la venta
    
    # ==========================================
    # CAMPOS AVANZADOS (OPCIONALES)
    # ==========================================
    forma_pago: Optional[PaymentTerms] = None  # OPCIONAL: Forma de pago (Contado/Crédito)
    cuotas: List[Cuota] = field(default_factory=list)  # OPCIONAL: Cuotas de pago
    
    # Campos adicionales opcionales
    observacion: str = ""               # OPCIONAL: Observaciones del documento
    tipo_operacion: str = "0101"        # OPCIONAL: Tipo de operación SUNAT
    
    def __post_init__(self):
        """Validaciones automáticas después de crear el objeto."""
        # Validar campos obligatorios
        if not self.company:
            raise ValueError("Company es requerido")
        if not self.client:
            raise ValueError("Client es requerido")
            
        print(f"[{self.__class__.__name__}] Comprobante creado: {self.get_nombre()}")
        
        # Validaciones SUNAT están en validator/ - core es declarativo
        # self._validar_documento_sunat() -> MoveToDifferentLayer
        
        # Campos ya están en snake_case - no necesita sincronización
        
        # Greenter es declarativo - NO recalcula totales automáticamente
        # Los totales deben ser proporcionados por el usuario
        # Las series son libres según SUNAT - no hay restricciones específicas
    
    # Validaciones están en validator/ - core es declarativo como greenter
    # def _validar_documento_sunat(self): -> MoveToDifferentLayer

    def get_nombre(self) -> str:
        """Obtiene el nombre completo del comprobante."""
        # Acepta tanto enteros como strings para correlativo
        if isinstance(self.correlativo, int):
            # Para enteros, usar formato con ceros a la izquierda según necesidad
            correlativo_str = str(self.correlativo).zfill(8)
        else:
            # Para strings, usar tal cual (ya debería venir formateado)
            correlativo_str = str(self.correlativo)
        return f"{self.company.ruc}-{self.tipo_doc}-{self.serie}-{correlativo_str}"
    
    # Greenter es 100% declarativo - NO calcula totales ni crea leyendas automáticamente
    # Usuario debe proporcionar todos los valores y leyendas manualmente
    
    def agregar_detalle(self, detalle: SaleDetail):
        """Agregar un detalle (sin recalcular totales automáticamente)."""
        self.details.append(detalle)
        print(f"[{self.__class__.__name__}] Detalle agregado: {detalle.descripcion} - Cantidad: {detalle.cantidad}")
        # Greenter es declarativo - usuario debe proporcionar totales manualmente
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Debe ser implementado por las clases hijas."""
        pass