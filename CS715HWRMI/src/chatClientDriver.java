import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.UnknownHostException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.Scanner;

public class chatClientDriver {

	public static void main(String[] args) throws RemoteException {
		// argv[0]: hostname/localname
				// argv[1]: portname
				
				//InetAddress host =InetAddress.getLocalHost();
		
		 chatServerInterface serverRO = null;
				try {
					
				 //InetAddress host = InetAddress.getByName(args[0]);//server ---localhost
				    String host = args[0];
					 int port =Integer.parseInt(args[1]) ;//server---9000
					 Registry regis = LocateRegistry.getRegistry("localhost",port);
					 String serverurl= "rmi://"+host+":"+port+"/ro";
					  serverRO =(chatServerInterface) regis.lookup(serverurl);
				    } catch (RemoteException e) 
				      {e.printStackTrace();} 
				      catch (NotBoundException e) {
						e.printStackTrace();}
		            
				System.out.println("please type the client name ");
			    Scanner sc = new  Scanner(System.in);// Create a Scanner object
			    String clientname =sc.nextLine();  
			    String msg;
			    chatClientInterface newclient = null;
			    newclient = new chatClientRemoteObject(clientname,serverRO);
			    newclient.StartServer();
			    System.out.println("please send your message,if you want to exit,type exit please ");
			    Scanner scan = new  Scanner(System.in);// Create a Scanner object
			    while(true)
			    {
		
			    	 msg = scan.nextLine();
			    	if (msg.equals("exit"))
			          {newclient.exitServer();
			    		break;}
			    	newclient.sendMessage(msg);//sendmessage method implement stub.server method
			    }
				

	}

}
