import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.ArrayList;

public class chatServerRemoteObject extends UnicastRemoteObject implements chatServerInterface{
	ArrayList<chatClientInterface> clientList;
	static int id =1;
	protected chatServerRemoteObject() throws RemoteException {
		//UnicastRemoteObject.exportObject(this, 0);
		clientList = new ArrayList<chatClientInterface>();
	}
	
	public void boardcasToAll(String message) throws RemoteException {
		int i = 0;
		while(i<clientList.size())
			clientList.get(i++).receiveMessage(message);
		 System.out.println(message);
	}

	public void welcome(String clientname) throws RemoteException {
		chatClientInterface client = null;
		try {
			  Registry regis = LocateRegistry.getRegistry(9000);
			  client = (chatClientInterface)regis.lookup(clientname);
			  
		} catch (RemoteException e) {
			e.printStackTrace();
		} catch (NotBoundException e) {
			e.printStackTrace();
		}
		
		this.clientList.add(client);
		boardcasToAll("Welcome our new client "+clientname);
		boardcasToAll(clientname+"'s id is "+id);
	    
	    id++;    
}
	
	
	public void clientToAll(String message) throws RemoteException {
		  boardcasToAll(message);
		  System.out.println(message);
	}
	
	@Override
	public void removeClient(chatClientInterface c) throws RemoteException {
		 if (this.clientList.remove(c))	 
			 {id--;
			 System.out.println(c.name+" left the chatroom ");}
		 else
			 System.out.println(" client "+c.name+" is not found ");
		
	}

	

}
