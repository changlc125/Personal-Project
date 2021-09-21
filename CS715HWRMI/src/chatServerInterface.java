import java.rmi.Remote;
import java.rmi.RemoteException;

public interface chatServerInterface extends Remote{
	
		void boardcasToAll(String message) throws RemoteException;
		
		void welcome(String clientName) throws RemoteException;

		void clientToAll(String message)throws RemoteException;
		
		void removeClient(chatClientInterface c) throws RemoteException;
		
	}


