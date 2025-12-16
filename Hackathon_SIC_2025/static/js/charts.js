class FinancialCharts {
    constructor() {
        this.data = window.financialData;
        this.initialized = false;
        console.log('📊 FinancialCharts inicializado con datos reales:', this.data);
    }

    initialize() {
        if (this.initialized) return;
        
        console.log('🎯 Inicializando gráficos con datos reales...');
     
        // Esperar a que los tabs estén listos
        setTimeout(() => {
            this.createHorizontalAnalysisChart();
            this.createVerticalAnalysisCharts();
            this.createRazonesRadarChart();
            this.createPuntoEquilibrioChart();
            this.createGrowthChart();
            this.initialized = true;
            console.log('✅ Todos los gráficos con datos reales inicializados');
        }, 1000);
    }

    createHorizontalAnalysisChart() {
        const ctx = document.getElementById('graficoHorizontal');
        if (!ctx || !this.data.resultados.horizontal) {
            console.log('❌ No hay datos para gráfico horizontal');
            return;
        }

        try {
            const horizontalData = this.data.resultados.horizontal;
            const labels = [];
            const data = [];

            // Extraer datos del análisis horizontal REAL
            for (const [key, value] of Object.entries(horizontalData)) {
                if (key !== 'utilidad_neta' && value.variacion_porcentual !== undefined) {
                    labels.push(this.formatLabel(key));
                    data.push(value.variacion_porcentual);
                }
            }

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Variación %',
                        data: data,
                        backgroundColor: data.map(val => 
                            val > 0 ? 'rgba(40, 167, 69, 0.8)' : 'rgba(220, 53, 69, 0.8)'
                        ),
                        borderColor: data.map(val => 
                            val > 0 ? 'rgb(40, 167, 69)' : 'rgb(220, 53, 69)'
                        ),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Análisis Horizontal - Variaciones Porcentuales'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Variación: ${context.parsed.y.toFixed(1)}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Variación %'
                            }
                        }
                    }
                }
            });
            console.log('✅ Gráfico horizontal creado con datos reales');
        } catch (error) {
            console.error('❌ Error creando gráfico horizontal:', error);
        }
    }

    createVerticalAnalysisCharts() {
        this.createVerticalERChart();
        this.createVerticalBGChart();
        this.createEstructuraFinancieraChart();
    }

    createVerticalERChart() {
        const ctx = document.getElementById('graficoVerticalER');
        if (!ctx || !this.data.resultados.vertical) {
            console.log('❌ No hay datos para gráfico vertical ER');
            return;
        }

        try {
            const verticalData = this.data.resultados.vertical.estado_resultados;
            const labels = [];
            const data = [];

            for (const [key, value] of Object.entries(verticalData)) {
                labels.push(this.formatLabel(key));
                data.push(value);
            }

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            'rgba(220, 53, 69, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(108, 117, 125, 0.8)',
                            'rgba(40, 167, 69, 0.8)',
                            'rgba(0, 123, 255, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Composición Estado de Resultados (%)'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.label}: ${context.parsed.toFixed(1)}%`;
                                }
                            }
                        }
                    }
                }
            });
            console.log('✅ Gráfico vertical ER creado con datos reales');
        } catch (error) {
            console.error('❌ Error creando gráfico vertical ER:', error);
        }
    }

    createVerticalBGChart() {
        const ctx = document.getElementById('graficoVerticalBG');
        if (!ctx || !this.data.resultados.vertical) {
            console.log('❌ No hay datos para gráfico vertical BG');
            return;
        }

        try {
            const verticalData = this.data.resultados.vertical.balance_general;
            const labels = [];
            const data = [];

            for (const [key, value] of Object.entries(verticalData)) {
                labels.push(this.formatLabel(key));
                data.push(value);
            }

            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            'rgba(0, 123, 255, 0.8)',
                            'rgba(23, 162, 184, 0.8)',
                            'rgba(111, 66, 193, 0.8)',
                            'rgba(253, 126, 20, 0.8)',
                            'rgba(40, 167, 69, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Composición Balance General (%)'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.label}: ${context.parsed.toFixed(1)}%`;
                                }
                            }
                        }
                    }
                }
            });
            console.log('✅ Gráfico vertical BG creado con datos reales');
        } catch (error) {
            console.error('❌ Error creando gráfico vertical BG:', error);
        }
    }

    createEstructuraFinancieraChart() {
        const ctx = document.getElementById('graficoEstructuraFinanciera');
        if (!ctx || !this.data.resultados.vertical) return;

        try {
            const estructura = this.data.resultados.vertical.estructura_financiera;
            if (!estructura) return;

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Estructura'],
                    datasets: [
                        {
                            label: 'Pasivos',
                            data: [estructura.pasivos_porcentaje || 0],
                            backgroundColor: 'rgba(220, 53, 69, 0.8)',
                            borderColor: 'rgba(220, 53, 69, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Patrimonio',
                            data: [estructura.patrimonio_porcentaje || 0],
                            backgroundColor: 'rgba(40, 167, 69, 0.8)',
                            borderColor: 'rgba(40, 167, 69, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Composición Financiera'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.parsed.x}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            stacked: true,
                            max: 100,
                            ticks: { callback: value => value + '%' }
                        },
                        y: {
                            stacked: true,
                            display: false // Ocultar labels del eje Y
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error en gráfico estructura:', error);
        }
    }

    createRazonesRadarChart() {
        const ctx = document.getElementById('graficoRadarRazones');
        if (!ctx || !this.data.resultados.razones) {
            console.log('❌ No hay datos para gráfico radar');
            return;
        }

        try {
            const razones = this.data.resultados.razones;
            const puntoEquilibrio = this.data.resultados.punto_equilibrio;
            
            const labels = ['Liquidez', 'ROA', 'ROE', 'Endeudamiento'];
            const dataActual = [
                razones.liquidez_corriente || 0,
                razones.roa || 0,
                razones.roe || 0,
                razones.endeudamiento || 0
            ];

            // Agregar margen de seguridad si está disponible
            if (puntoEquilibrio && puntoEquilibrio.margen_seguridad_porcentaje) {
                labels.push('Margen Seguridad');
                dataActual.push(puntoEquilibrio.margen_seguridad_porcentaje);
            }

            const dataMeta = dataActual.map(() => 0).map((_, index) => {
                // Metas ideales aproximadas
                const metas = [2.0, 15.0, 20.0, 40.0, 20.0];
                return metas[index] || 20;
            });

            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Indicadores Actuales',
                        data: dataActual,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)'
                    }, {
                        label: 'Meta Ideal',
                        data: dataMeta,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Comparativa de Indicadores vs Meta Ideal'
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('✅ Gráfico radar creado con datos reales');
        } catch (error) {
            console.error('❌ Error creando gráfico radar:', error);
        }
    }

    createPuntoEquilibrioChart() {
        const ctx = document.getElementById('graficoPuntoEquilibrio');
        if (!ctx || !this.data.resultados.punto_equilibrio) {
            console.log('❌ No hay datos para gráfico punto equilibrio');
            return;
        }

        try {
            const eq = this.data.resultados.punto_equilibrio;
            const puntoEqUnidades = eq.punto_equilibrio_unidades || 0;
            const maxUnidades = Math.max(puntoEqUnidades * 1.5, 2000);
            
            const unidades = [];
            const costosFijos = [];
            const costosVariables = [];
            const costosTotales = [];
            const ingresos = [];

            for (let u = 0; u <= maxUnidades; u += Math.round(maxUnidades / 10)) {
                unidades.push(u);
                costosFijos.push(eq.costos_fijos || 0);
                costosVariables.push(u * (eq.costo_variable || 0));
                costosTotales.push(costosFijos[costosFijos.length - 1] + costosVariables[costosVariables.length - 1]);
                ingresos.push(u * (eq.precio_venta || 0));
            }

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: unidades,
                    datasets: [{
                        label: 'Costos Fijos',
                        data: costosFijos,
                        borderColor: 'rgba(108, 117, 125, 1)',
                        borderDash: [5, 5],
                        fill: false
                    }, {
                        label: 'Costos Totales',
                        data: costosTotales,
                        borderColor: 'rgba(220, 53, 69, 1)',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: true
                    }, {
                        label: 'Ingresos',
                        data: ingresos,
                        borderColor: 'rgba(40, 167, 69, 1)',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Análisis de Punto de Equilibrio'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Unidades Vendidas'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Quetzales (Q)'
                            },
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('✅ Gráfico punto equilibrio creado con datos reales');
        } catch (error) {
            console.error('❌ Error creando gráfico punto equilibrio:', error);
        }
    }

    createGrowthChart() {
        const ctx = document.getElementById('graficoCrecimiento');
        if (!ctx || !this.data.resultados.horizontal) {
            console.log('❌ No hay datos para gráfico crecimiento');
            return;
        }

        try {
            const horizontal = this.data.resultados.horizontal;
            const ventasAnterior = horizontal['Ventas totales']?.año_anterior || 0;
            const ventasActual = horizontal['Ventas totales']?.año_actual || 0;
            const utilidadAnterior = horizontal.utilidad_neta?.año_anterior || 0;
            const utilidadActual = horizontal.utilidad_neta?.año_actual || 0;

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Año Anterior', 'Año Actual'],
                    datasets: [{
                        label: 'Ventas',
                        data: [ventasAnterior, ventasActual],
                        backgroundColor: 'rgba(54, 162, 235, 0.8)'
                    }, {
                        label: 'Utilidad Neta',
                        data: [utilidadAnterior, utilidadActual],
                        backgroundColor: 'rgba(75, 192, 192, 0.8)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Evolución de Ventas y Utilidades'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'Q' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
            console.log('✅ Gráfico crecimiento creado con datos reales');
        } catch (error) {
            console.error('❌ Error creando gráfico crecimiento:', error);
        }
    }

    formatLabel(label) {
        const labelsMap = {
            'Ventas totales': 'Ventas',
            'Otros ingresos': 'Otros Ingresos',
            'Costo de ventas': 'Costo Ventas',
            'Gastos de operación': 'Gastos Operación',
            'Gastos financieros': 'Gastos Financieros',
            'Efectivo y bancos': 'Efectivo',
            'Cuentas por cobrar': 'Cuentas Cobrar',
            'Activos fijos': 'Activos Fijos'
        };
        return labelsMap[label] || label;
    }
}

// Inicialización global
let financialCharts;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM cargado, verificando datos para gráficos...');
    
    if (window.financialData && window.financialData.resultados) {
        financialCharts = new FinancialCharts();
        
        // Inicializar cuando se cambie de tab
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', function() {
                console.log('🔄 Tab cambiado, reinicializando gráficos...');
                setTimeout(() => financialCharts.initialize(), 300);
            });
        });
        
        // Inicializar inmediatamente
        financialCharts.initialize();
    } else {
        console.warn('⚠️ No se encontraron datos financieros para gráficos');
    }
});