#include "StationOpeningWidget.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "Framework/Application/SlateApplication.h"
#include "Fonts/FontMeasure.h"
#include "Rendering/SlateRenderer.h"

int32 UStationOpeningWidget::NativePaint(const FPaintArgs& Args,const FGeometry& G,const FSlateRect& CullingRect,FSlateWindowElementList& Out,int32 Layer,const FWidgetStyle& Style,bool bParentEnabled) const
{
 Layer=Super::NativePaint(Args,G,CullingRect,Out,Layer,Style,bParentEnabled);
 const FVector2D Size=G.GetLocalSize();
 const auto Ramp=[](float T,float A,float B){return FMath::SmoothStep(A,B,T);};
 const float Black=1-Ramp(Elapsed,4.3f,6.0f);
 const FSlateBrush* Brush=FCoreStyle::Get().GetBrush("WhiteBrush");
 if(Black>0)FSlateDrawElement::MakeBox(Out,++Layer,G.ToPaintGeometry(),Brush,ESlateDrawEffect::None,FLinearColor(.006f,.009f,.012f,Black));
 auto Text=[&](const FString& Value,float Y,int32 FontSize,FLinearColor Color)
 {
  const FSlateFontInfo Font=FCoreStyle::GetDefaultFontStyle("Regular",FontSize);
  const FVector2D Extent=FSlateApplication::Get().GetRenderer()->GetFontMeasureService()->Measure(Value,Font);
  FSlateDrawElement::MakeText(Out,++Layer,G.ToPaintGeometry(Extent,FSlateLayoutTransform(FVector2D((Size.X-Extent.X)*.5f,Y))),Value,Font,ESlateDrawEffect::None,Color);
 };
 const float Title=Ramp(Elapsed,.35f,1.65f)*(1-Ramp(Elapsed,3.6f,5.1f));
 if(Title>0)
 {
  const int32 FontSize=FMath::Clamp(FMath::RoundToInt(Size.X*.040f),18,64);
  Text(TEXT("MALDEK STATION"),Size.Y*.43f,FontSize,FLinearColor(.85f,.89f,.88f,Title));
  const FVector2D LineSize(FMath::Min(Size.X*.12f,180.0f),1.0f);
  FSlateDrawElement::MakeBox(Out,++Layer,G.ToPaintGeometry(LineSize,FSlateLayoutTransform(FVector2D((Size.X-LineSize.X)*.5f,Size.Y*.43f+FontSize*1.7f))),Brush,ESlateDrawEffect::None,FLinearColor(.43f,.51f,.49f,Title*.55f));
 }
 const float Hint=Ramp(Elapsed,6.2f,7.2f)*(1-Ramp(Elapsed,HintEnd-1,HintEnd));
 if(Hint>0)
 {
  const float Width=FMath::Min(Size.X*.88f,620.0f),Top=Size.Y*.77f;
  FSlateDrawElement::MakeBox(Out,++Layer,G.ToPaintGeometry(FVector2D(Width,100),FSlateLayoutTransform(FVector2D((Size.X-Width)*.5f,Top))),Brush,ESlateDrawEffect::None,FLinearColor(.008f,.012f,.014f,Hint*.8f));
  const int32 FontSize=FMath::Clamp(FMath::RoundToInt(Size.X*.014f),12,20);
  Text(TEXT("F   Flashlight on / off"),Top+17,FontSize,bToggled?FLinearColor(.53f,.8f,.65f,Hint):FLinearColor(.9f,.93f,.92f,Hint));
  Text(TEXT("SCROLL   Up: tighter beam    Down: wider beam"),Top+53,FontSize,bFocused?FLinearColor(.53f,.8f,.65f,Hint):FLinearColor(.75f,.83f,.81f,Hint));
 }
 return Layer;
}
