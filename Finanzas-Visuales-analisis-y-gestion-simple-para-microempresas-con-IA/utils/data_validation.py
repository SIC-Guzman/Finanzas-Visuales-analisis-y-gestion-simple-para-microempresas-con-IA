import pandas as pd
import os
from typing import Dict, Any

class ValidadorDatos:
    def __init__(self):
        self.errores = []
        self.advertencias = []
    
    def validar_archivo(self, archivo_path: str) -> Dict[str, Any]:
        """
        Valida y detecta el tipo de archivo, luego lo carga
        """
        self.errores = []
        self.advertencias = []
        
        if not os.path.exists(archivo_path):
            self.errores.append(f"El archivo {archivo_path} no existe")
            return {}
        
        # Detectar tipo de archivo
        tipo_archivo = self._detectar_tipo_archivo(archivo_path)
        print(f"📄 Tipo de archivo detectado: {tipo_archivo}")
        
        if tipo_archivo == 'excel_multihoja':
            return self._cargar_excel_multihoja(archivo_path)
        elif tipo_archivo == 'excel_unahoja':
            return self._cargar_excel_unahoja(archivo_path)
        elif tipo_archivo == 'csv':
            return self._cargar_csv(archivo_path)
        else:
            self.errores.append("Formato de archivo no soportado")
            return {}
    
    def _detectar_tipo_archivo(self, archivo_path: str) -> str:
        """
        Detecta el tipo de archivo basado en extensión y estructura
        """
        if archivo_path.endswith('.csv'):
            return 'csv'
        elif archivo_path.endswith(('.xlsx', '.xls')):
            # Verificar si es multi-hoja
            try:
                excel_file = pd.ExcelFile(archivo_path)
                hojas_esperadas = ['estado_resultados', 'balance_general', 'datos_equilibrio', 'Datos_empresa']
                hojas_encontradas = [hoja for hoja in excel_file.sheet_names if hoja in hojas_esperadas]
                
                print(f"📊 Hojas encontradas: {excel_file.sheet_names}")
                print(f"📊 Hojas esperadas encontradas: {hojas_encontradas}")
                
                if len(hojas_encontradas) >= 3:
                    return 'excel_multihoja'
                else:
                    return 'excel_unahoja'
            except Exception as e:
                print(f"⚠️  Error detectando tipo Excel: {e}")
                return 'excel_unahoja'
        else:
            return 'desconocido'
    
    def _cargar_excel_multihoja(self, archivo_path: str) -> Dict[str, Any]:
        """
        Carga archivo Excel con estructura multi-hoja
        """
        try:
            datos = {
                'estado_resultados': pd.read_excel(archivo_path, sheet_name='estado_resultados'),
                'balance_general': pd.read_excel(archivo_path, sheet_name='balance_general'),
                'datos_equilibrio': pd.read_excel(archivo_path, sheet_name='datos_equilibrio'),
                'datos_empresa': pd.read_excel(archivo_path, sheet_name='Datos_empresa'),
                'tipo_archivo': 'excel_multihoja'
            }
            
            print("✅ Excel multi-hoja cargado exitosamente")
            
            # Validar estructura básica
            self._validar_estructura_multihoja(datos)
            
            return datos
            
        except Exception as e:
            self.errores.append(f"Error cargando Excel multi-hoja: {str(e)}")
            return {}
    
    def _cargar_excel_unahoja(self, archivo_path: str) -> Dict[str, Any]:
        """
        Carga archivo Excel de una sola hoja con estructura consolidada
        """
        try:
            # Leer todo el Excel
            df = pd.read_excel(archivo_path)
            print(f"📊 DataFrame cargado. Shape: {df.shape}")
            
            # Parsear la hoja única
            datos = self._parsear_hoja_unica(df)
            datos['tipo_archivo'] = 'excel_unahoja'
            
            print("✅ Excel hoja única procesado")
            
            return datos
            
        except Exception as e:
            self.errores.append(f"Error cargando Excel hoja única: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _cargar_csv(self, archivo_path: str) -> Dict[str, Any]:
        """
        Carga archivo CSV estructurado
        """
        try:
            df = pd.read_csv(archivo_path)
            print(f"📊 CSV cargado. Shape: {df.shape}")
            
            # Parsear CSV (estructura similar a hoja única)
            datos = self._parsear_hoja_unica(df)
            datos['tipo_archivo'] = 'csv'
            
            return datos
            
        except Exception as e:
            self.errores.append(f"Error cargando CSV: {str(e)}")
            return {}
    
    def _parsear_hoja_unica(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parsea un DataFrame de hoja única a la estructura esperada
        VERSIÓN MEJORADA para tu estructura específica
        """
        datos = {
            'estado_resultados': pd.DataFrame(),
            'balance_general': pd.DataFrame(),
            'datos_equilibrio': pd.DataFrame(),
            'datos_empresa': pd.DataFrame()
        }
        
        try:
            print("🔄 Iniciando parseo MEJORADO de hoja única...")
            print(f"📊 DataFrame shape: {df.shape}")
            print(f"📊 Columnas: {df.columns.tolist()}")
            
            # ESTRATEGIA MEJORADA: Buscar secciones por headers específicos
            secciones = {
                'datos_empresa': ['NOMBRE DE LA EMPRESA', 'TIPO DE NEGOCIO', 'MONEDA'],
                'estado_resultados': ['VENTAS TOTALES', 'COSTO DE VENTAS', 'GASTOS DE OPERACIÓN'],
                'balance_general': ['EFECTIVO Y BANCOS', 'CUENTAS POR COBRAR', 'INVENTARIOS'],
                'datos_equilibrio': ['PRECIO DE VENTA UNITARIO', 'COSTO VARIABLE UNITARIO', 'COSTOS FIJOS MENSUALES']
            }
            
            for seccion, keywords in secciones.items():
                datos[seccion] = self._extraer_seccion_por_keywords(df, keywords)
                print(f"✅ {seccion}: {datos[seccion].shape}")
            
            # Si alguna sección está vacía, usar estrategia de fallback
            if datos['estado_resultados'].empty and datos['balance_general'].empty:
                print("⚠️  Usando estrategia de fallback mejorada")
                datos = self._estrategia_fallback_mejorada(df)
            
            print("✅ Parseo MEJORADO de hoja única completado")
            return datos
            
        except Exception as e:
            print(f"❌ Error parseando hoja única: {str(e)}")
            import traceback
            traceback.print_exc()
            return datos

    def _extraer_seccion_por_keywords(self, df: pd.DataFrame, keywords: list) -> pd.DataFrame:
        """Extrae una sección basado en keywords específicos"""
        try:
            for idx in range(len(df)):
                fila_str = ' '.join([str(x) for x in df.iloc[idx] if pd.notna(x)])
                
                # Buscar fila que contenga ALGUNO de los keywords
                if any(keyword in fila_str.upper() for keyword in keywords):
                    print(f"🔍 Encontrada sección en fila {idx}: {fila_str[:50]}...")
                    
                    # Tomar un rango de filas alrededor del keyword
                    inicio = max(0, idx - 1)  # Incluir header
                    fin = min(len(df), idx + 12)  # Tomar hasta 12 filas
                    
                    seccion_df = df.iloc[inicio:fin].copy()
                    print(f"📋 Sección extraída: {seccion_df.shape}")
                    return seccion_df
                    
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error extrayendo sección: {e}")
            return pd.DataFrame()

    def _estrategia_fallback_mejorada(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Estrategia de fallback mejorada para hoja única"""
        datos = {
            'estado_resultados': pd.DataFrame(),
            'balance_general': pd.DataFrame(),
            'datos_equilibrio': pd.DataFrame(),
            'datos_empresa': pd.DataFrame()
        }
        
        # Buscar por nombres de columnas conocidos
        for col in df.columns:
            col_str = str(col).upper()
            
            if 'AÑO_ANTERIOR' in col_str or 'AÑO_ACTUAL' in col_str:
                # Es estado de resultados o balance general
                columnas_interes = []
                for col_df in df.columns:
                    if any(keyword in str(col_df).upper() for keyword in ['CONCEPTO', 'AÑO_ANTERIOR', 'AÑO_ACTUAL']):
                        columnas_interes.append(col_df)
                
                if columnas_interes:
                    datos['estado_resultados'] = df[columnas_interes].dropna(how='all').head(20)
            
            elif 'VALOR' in col_str:
                # Es datos de equilibrio
                columnas_interes = []
                for col_df in df.columns:
                    if any(keyword in str(col_df).upper() for keyword in ['CONCEPTO', 'VALOR']):
                        columnas_interes.append(col_df)
                
                if columnas_interes:
                    datos['datos_equilibrio'] = df[columnas_interes].dropna(how='all').head(10)
        
        # Datos de empresa - primeras filas que no sean numéricas
        if datos['datos_empresa'].empty:
            datos['datos_empresa'] = df.head(8).copy()
        
        return datos
    
    def _extraer_por_columnas(self, df: pd.DataFrame, columnas_buscar: list) -> pd.DataFrame:
        """Extrae datos basado en nombres de columnas"""
        try:
            columnas_encontradas = []
            for col_buscar in columnas_buscar:
                for col_df in df.columns:
                    if col_buscar in str(col_df).upper():
                        columnas_encontradas.append(col_df)
                        break
            
            if columnas_encontradas:
                return df[columnas_encontradas].copy()
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def _buscar_seccion_por_contenido(self, df: pd.DataFrame, keywords: list) -> pd.DataFrame:
        """Busca una sección por contenido de filas"""
        try:
            for idx in range(len(df)):
                fila_str = ' '.join([str(x) for x in df.iloc[idx] if pd.notna(x)])
                if any(keyword.upper() in fila_str.upper() for keyword in keywords):
                    # Encontramos una fila con keywords, tomar 10 filas a partir de aquí
                    inicio = max(0, idx - 2)
                    fin = min(len(df), idx + 10)
                    return df.iloc[inicio:fin].copy()
            
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def _formatear_datos_empresa(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatea datos de empresa"""
        if len(df.columns) >= 2:
            return df.iloc[:, :2].dropna()
        return pd.DataFrame()
    
    def _formatear_estado_resultados(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatea estado de resultados"""
        for idx, fila in df.iterrows():
            primera_columna = fila.iloc[0] if len(fila) > 0 else None
            if pd.notna(primera_columna) and any(palabra in str(primera_columna).upper() for palabra in ['CONCEPTO', 'DESCRIPCIÓN']):
                return df.iloc[idx:].reset_index(drop=True)
        return df
    
    def _formatear_balance_general(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatea balance general"""
        return self._formatear_estado_resultados(df)
    
    def _formatear_datos_equilibrio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatea datos de equilibrio"""
        return df
    
    def _validar_estructura_multihoja(self, datos: Dict[str, Any]):
        """Valida la estructura de archivos multi-hoja"""
        hojas_requeridas = ['estado_resultados', 'balance_general', 'datos_equilibrio']
        
        for hoja in hojas_requeridas:
            if hoja not in datos or datos[hoja].empty:
                self.advertencias.append(f"Hoja '{hoja}' está vacía o no encontrada")
    
    def obtener_errores(self) -> list:
        """Retorna lista de errores"""
        return self.errores
    
    def obtener_advertencias(self) -> list:
        """Retorna lista de advertencias"""
        return self.advertencias
    
    def es_valido(self) -> bool:
        """Verifica si los datos son válidos"""
        return len(self.errores) == 0

# FUNCIÓN INDEPENDIENTE - debe estar FUERA de la clase
def validar_y_cargar_archivo(archivo_path: str) -> Dict[str, Any]:
    """
    Función simple para validar y cargar archivo
    """
    validador = ValidadorDatos()
    datos = validador.validar_archivo(archivo_path)
    
    return {
        'datos': datos,
        'errores': validador.obtener_errores(),
        'advertencias': validador.obtener_advertencias(),
        'es_valido': validador.es_valido()
    }