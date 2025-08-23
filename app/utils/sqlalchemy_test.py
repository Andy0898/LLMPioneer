from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

# 创建引擎和基础模型
engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
metadata = MetaData()

# 用户和地址表（无物理外键）
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # 使用 backref 创建双向关系
    addresses_backref = relationship(
        "Address", 
        backref="user_backref",
        primaryjoin="User.id == Address.user_id",  # 手动指定连接条件
        foreign_keys="Address.user_id"  # 手动指定外键（逻辑上的）
    )
    
    # 使用 back_populates 创建双向关系
    addresses_populates = relationship(
        "Address", 
        back_populates="user_populates",
        primaryjoin="User.id == Address.user_id",
        foreign_keys="Address.user_id"
    )

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer)  # 无物理外键约束
    
    # 配合 User.addresses_populates
    user_populates = relationship(
        "User", 
        back_populates="addresses_populates",
        primaryjoin="User.id == Address.user_id",
        foreign_keys="Address.user_id"
    )

# 创建表（无物理外键约束）
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# 测试 backref
user1 = User(name="Alice")
address1 = Address(email="alice@example.com")
user1.addresses_backref.append(address1)
session.add_all([user1, address1])
session.commit()

# 验证双向关系（backref）
print(address1.user_backref.name)  # 输出: Alice
print(user1.addresses_backref[0].email)  # 输出: alice@example.com

# 测试 back_populates
user2 = User(name="Bob")
address2 = Address(email="bob@example.com")
user2.addresses_populates.append(address2)
session.add_all([user2, address2])
session.commit()

# 验证双向关系（back_populates）
print(address2.user_populates.name)  # 输出: Bob
print(user2.addresses_populates[0].email)  # 输出: bob@example.com