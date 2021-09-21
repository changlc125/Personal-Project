import java.net.InetAddress;
import java.net.UnknownHostException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class chatServerDriver  {
	public static void main(String args[]) 
	{
		// argv[0]: hostname/localname
		// argv[1]: portname
		
		//InetAddress host =InetAddress.getLocalHost();
		try {
			//InetAddress host = InetAddress.getByName(args[0]);//localhost
			  String host = args[0];
			 int port =Integer.parseInt(args[1]) ;//9000
			chatServerInterface ro = new chatServerRemoteObject();
			Registry regisry = LocateRegistry.createRegistry( port );
			String serverurl ="rmi://"+host+":"+port+"/ro";
			regisry.rebind(serverurl, ro);
			System.out.println("[System] Chat Server is ready.");
		    } catch (RemoteException e) 
		      {System.out.println("Chat Server failed: " + e);}
            
		
		}
	
	
}
