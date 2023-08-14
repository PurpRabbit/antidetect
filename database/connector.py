from sqlalchemy import create_engine, update, delete, select
from sqlalchemy.orm import sessionmaker

from database.models import ProfileModel, ProxyModel, Base


class SqlDatabase:
    def __init__(self, db_name):
        """
        Initializes the SqlDatabase class by creating a database connection and session.

        """
        engine = create_engine(f'sqlite:///{db_name}')
        Session = sessionmaker(bind=engine)
        self.session = Session()

        Base.metadata.create_all(engine)

    def get_profiles(self) -> list[ProfileModel]:
        """
        Retrieves all profile records from the database.

        Returns:
            list[ProfileModel]: List of ProfileModel objects representing profiles.

        """
        return self.session.query(ProfileModel).all()

    def get_profile(self, name: str) -> ProfileModel:
        """
        Retrieves a specific profile record from the database based on the provided name.

        Args:
            name (str): Name of the profile.

        Returns:
            ProfileModel: ProfileModel object representing the profile.

        """
        query = select(ProfileModel).where(ProfileModel.name == name)
        return self.session.execute(query).first()[0]

    def create_profile(self, name: str, user_agent: str, proxy_id: int = None, description: str = None) -> None:
        """
        Creates a new profile record in the database.

        Args:
            name (str): Name of the profile.
            user_agent (str): User agent string for the profile.
            proxy_id (int, optional): ID of the associated proxy. Defaults to None.
            description (str, optional): Description of the profile. Defaults to None.

        """
        new_profile = ProfileModel(name=name, user_agent=user_agent, proxy_id=proxy_id, description=description)
        self.session.add(new_profile)
        self.session.commit()

    def change_proxy_valid(self, server: str, is_valid: bool) -> None:
        """
        Changes the validity status of a specific proxy.

        Args:
            server (str): Proxy server address.
            is_valid (bool): Validity status of the proxy.

        """
        query = update(ProxyModel).where(ProxyModel.server == server).values(is_valid=is_valid)
        self.session.execute(query)
        self.session.commit()

    def delete_profile(self, name: str) -> None:
        """
        Deletes a specific profile from the database.

        Args:
            name (str): Name of the profile to be deleted.

        """
        query = delete(ProfileModel).where(ProfileModel.name == name)
        self.session.execute(query)
        self.session.commit()

    def delete_proxy(self, proxy_id: int) -> None:
        """
        Deletes a specific proxy from the database.

        Args:
            proxy_id (int): ID of the proxy to be deleted.

        """
        query = delete(ProxyModel).where(ProxyModel.id == proxy_id)
        self.session.execute(query)
        self.session.commit()

    def profile_prune(self):
        """
        Deletes all profile records from the database.

        """
        query = delete(ProfileModel)
        self.session.execute(query)
        self.session.commit()

    def proxy_prune(self):
        """
        Deletes all proxy records from the database.

        """
        query = delete(ProxyModel)
        self.session.execute(query)
        self.session.commit()

    def change_profile_proxy(self, name: str, proxy_id: int) -> None:
        """
        Changes the proxy associated with a specific profile.

        Args:
            name (str): Name of the profile.
            proxy_id (int): ID of the new proxy.

        """
        query = update(ProfileModel).where(ProfileModel.name == name).values(proxy_id=proxy_id)
        self.session.execute(query)
        self.session.commit()

    def change_profile_description(self, name: str, description: str) -> None:
        """
        Changes the description of a specific profile.

        Args:
            name (str): Name of the profile.
            description (str): New description for the profile.

        """
        query = update(ProfileModel).where(ProfileModel.name == name).values(description=description)
        self.session.execute(query)
        self.session.commit()

    def profile_exists(self, name: str) -> bool:
        """
        Checks if a profile with the given name exists in the database.

        Args:
            name (str): Name of the profile.

        Returns:
            bool: True if the profile exists, False otherwise.

        """
        query = select(ProfileModel).where(ProfileModel.name == name)
        return self.session.execute(query).first() is not None

    def get_proxy(self, id: int) -> ProxyModel:
        """
        Retrieves a specific proxy from the database based on the provided ID.

        Args:
            id (int): ID of the proxy.

        Returns:
            ProxyModel: ProxyModel object representing the proxy.

        """
        query = select(ProxyModel).where(ProxyModel.id == id)
        return self.session.execute(query).first()[0]

    def proxy_exists(self, server: str) -> bool:
        """
        Checks if a proxy with the given server address exists in the database.

        Args:
            server (str): Proxy server address.

        Returns:
            bool: True if the proxy exists, False otherwise.

        """
        query = select(ProxyModel).where(ProxyModel.server == server)
        return self.session.execute(query).first() is not None

    def proxy_exists_by_id(self, id: int) -> bool:
        """
        Checks if a proxy with the given ID exists in the database.

        Args:
            id (int): ID of the proxy.

        Returns:
            bool: True if the proxy exists, False otherwise.

        """
        query = select(ProxyModel).where(ProxyModel.id == id)
        return self.session.execute(query).first() is not None

    def get_proxies(self) -> list[ProxyModel]:
        """
        Retrieves all proxy records from the database.

        Returns:
            list[ProxyModel]: List of ProxyModel objects representing proxies.

        """
        return self.session.query(ProxyModel).all()

    def create_proxy(self, server: str, country: str) -> None:
        """
        Creates a new proxy record in the database.

        Args:
            server (str): Proxy server address.
            country (str): Country associated with the proxy.

        """
        new_proxy = ProxyModel(server=server, country=country)
        self.session.add(new_proxy)
        self.session.commit()