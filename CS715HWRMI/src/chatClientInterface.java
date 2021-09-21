import java.rmi.Remote;
import java.rmi.RemoteException;

public interface chatClientInterface extends Remote{
	 String name =null;
	void sendMessage(String message) throws RemoteException;
	void receiveMessage(String message) throws RemoteException;
	void setName(String name) throws RemoteException;
	 String getName() throws RemoteException;
	 void exitServer() throws RemoteException;
	 void StartServer() throws RemoteException;
	
}
