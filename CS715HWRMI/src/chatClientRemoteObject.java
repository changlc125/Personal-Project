import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

public class chatClientRemoteObject extends UnicastRemoteObject implements chatClientInterface {
	chatServerInterface serverro;
	String name = null;
	
	protected chatClientRemoteObject(String name,chatServerInterface serverro) throws RemoteException {
		//UnicastRemoteObject.exportObject(this, 0);
		this.name = name;
		this.serverro= serverro;
		Registry regisry = LocateRegistry.getRegistry( "localhost",9000 );
		 regisry.rebind(this.name, this);
		 //serverro.welcome(name);
		 
	}

	
	
	
	public void sendMessage(String message) throws RemoteException {
		
		serverro.clientToAll(message);
		
	}

	
	public void receiveMessage(String message) throws RemoteException {
		System.out.println(message);
		
	}



	public void setName(String name) throws RemoteException {
		this.name = name;
	}


	
	public String getName() throws RemoteException {
		return name;
	}


	@Override
	public void exitServer() throws RemoteException {
		serverro.removeClient(this);
		
	}




	@Override
	public void StartServer() throws RemoteException {
		serverro.welcome(name);
		
	}
	
	
	
	

}
