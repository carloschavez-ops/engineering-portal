from datetime import datetime
from models import db


CATEGORIAS = [
    'Planificación de Recursos (MRP/ERP)',
    'Ventas y Clientes',
    'Finanzas y Contabilidad',
    'Operaciones',
    'Recursos Humanos',
    'Inventario y Logística',
    'Reportes y Analítica',
    'Herramientas Internas',
    'Sistemas Externos',
    'Otros',
]

ESTADOS = [
    ('disponible',    '🟢 Disponible'),
    ('mantenimiento', '🟡 En mantenimiento'),
    ('fuera',         '🔴 Fuera de servicio'),
]


class Application(db.Model):
    __tablename__ = 'applications'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nombre         = db.Column(db.String(150), nullable=False)
    url            = db.Column(db.String(500), nullable=False)
    descripcion    = db.Column(db.Text, default='')
    categoria      = db.Column(db.String(100), default='Otros')
    favorito       = db.Column(db.Boolean, default=False)
    icono          = db.Column(db.String(50), default='grid')
    color          = db.Column(db.String(20), default='#23486A')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado         = db.Column(db.String(20), default='disponible', nullable=False)

    history = db.relationship('History', backref='application',
                              lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_accesos(self):
        return self.history.count()

    @property
    def ultimo_acceso(self):
        from models.history import History as H
        last = self.history.order_by(H.fecha_acceso.desc()).first()
        return last.fecha_acceso if last else None

    @property
    def estado_badge(self):
        """Retorna (emoji, texto, clase_css) según el estado."""
        return {
            'disponible':    ('🟢', 'Disponible',        'estado--verde'),
            'mantenimiento': ('🟡', 'En mantenimiento',  'estado--amarillo'),
            'fuera':         ('🔴', 'Fuera de servicio', 'estado--rojo'),
        }.get(self.estado, ('🟢', 'Disponible', 'estado--verde'))

    def __repr__(self):
        return f'<Application {self.nombre}>'


from models.history import History  # noqa: E402