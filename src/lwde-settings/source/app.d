import gtk.Application : Application;
import gtk.ApplicationWindow;
import gtk.Box;
import gtk.HeaderBar;
import gtk.Label;
import gtk.ListBox;
import gtk.ListBoxRow;
import gtk.Paned;
import gtk.ScrolledWindow;
import gtk.Separator;
import gtk.Stack;
import gio.Application : GioApplication = Application;

ListBoxRow makeSidebarRow(string label)
{
    auto row = new ListBoxRow();
    auto box = new Box(Orientation.HORIZONTAL, 0);
    box.setMarginTop(8);
    box.setMarginBottom(8);
    box.setMarginStart(12);
    box.setMarginEnd(12);
    box.packStart(new Label(label), false, false, 0);
    row.add(box);
    return row;
}

class MainWindow : ApplicationWindow
{
    this(Application app)
    {
        super(app);
        setDefaultSize(800, 520);

        auto header = new HeaderBar();
        header.setShowCloseButton(true);
        header.setTitle("Settings");
        setTitlebar(header);

        auto stack = new Stack();
        stack.setTransitionType(StackTransitionType.SLIDE_UP_DOWN);
        stack.setTransitionDuration(150);

        auto generalPage = new Box(Orientation.VERTICAL, 12);
        generalPage.setMarginTop(24);
        generalPage.setMarginBottom(24);
        generalPage.setMarginStart(32);
        generalPage.setMarginEnd(32);
        auto generalHeading = new Label("<b><big>General</big></b>");
        generalHeading.setUseMarkup(true);
        generalHeading.setXalign(0);
        generalPage.packStart(generalHeading, false, false, 0);
        generalPage.packStart(new Separator(Orientation.HORIZONTAL), false, false, 0);
        stack.addNamed(generalPage, "general");

        auto networkPage = new Box(Orientation.VERTICAL, 12);
        networkPage.setMarginTop(24);
        networkPage.setMarginBottom(24);
        networkPage.setMarginStart(32);
        networkPage.setMarginEnd(32);
        auto networkHeading = new Label("<b><big>Network</big></b>");
        networkHeading.setUseMarkup(true);
        networkHeading.setXalign(0);
        networkPage.packStart(networkHeading, false, false, 0);
        networkPage.packStart(new Separator(Orientation.HORIZONTAL), false, false, 0);
        stack.addNamed(networkPage, "network");

        auto aboutPage = new Box(Orientation.VERTICAL, 12);
        aboutPage.setMarginTop(24);
        aboutPage.setMarginBottom(24);
        aboutPage.setMarginStart(32);
        aboutPage.setMarginEnd(32);
        auto aboutHeading = new Label("<b><big>About</big></b>");
        aboutHeading.setUseMarkup(true);
        aboutHeading.setXalign(0);
        aboutPage.packStart(aboutHeading, false, false, 0);
        aboutPage.packStart(new Separator(Orientation.HORIZONTAL), false, false, 0);
        auto versionLabel = new Label("Version 0.1");
        versionLabel.setXalign(0);
        aboutPage.packStart(versionLabel, false, false, 0);
        stack.addNamed(aboutPage, "about");

        auto listBox = new ListBox();
        listBox.setSelectionMode(SelectionMode.SINGLE);
        listBox.add(makeSidebarRow("General"));
        listBox.add(makeSidebarRow("Network"));
        listBox.add(makeSidebarRow("About"));

        listBox.selectRow(listBox.getRowAtIndex(0));
        stack.setVisibleChildName("general");

        immutable string[] names = ["general", "network", "about"];
        listBox.addOnRowSelected((ListBoxRow row, ListBox) {
            if (row !is null)
                stack.setVisibleChildName(names[row.getIndex()]);
        });

        auto sidebar = new Box(Orientation.VERTICAL, 0);
        sidebar.setSizeRequest(180, -1);

        auto sidebarScroll = new ScrolledWindow();
        sidebarScroll.setPolicy(PolicyType.NEVER, PolicyType.AUTOMATIC);
        sidebarScroll.add(listBox);
        sidebar.packStart(sidebarScroll, true, true, 0);

        auto contentScroll = new ScrolledWindow();
        contentScroll.setPolicy(PolicyType.NEVER, PolicyType.AUTOMATIC);
        contentScroll.add(stack);

        auto paned = new Paned(Orientation.HORIZONTAL);
        paned.pack1(sidebar, false, false);
        paned.pack2(contentScroll, true, true);
        paned.setPosition(180);

        add(paned);
        showAll();
    }
}

int main(string[] args)
{
    auto app = new Application("org.example.settings", GApplicationFlags.FLAGS_NONE);
    app.addOnActivate((GioApplication) { (new MainWindow(app)).present(); });
    return app.run(args);
}
